import json
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
import lxml.html

from vacancy_parse.scrapy import city_id_hh


def get_location_id(location_name):
    for area in city_id_hh['areas']:
        if area['name'].lower() == location_name.lower():
            return area['id']
    return None


def vacancy_search(request):
    if request.method == 'POST':
        job_title = request.POST.get('profile')
        job_location = request.POST.get('location')
        area = get_location_id(job_location)
        headhunter_jobs = None
        if area:
            headhunter_jobs = get_headhunter_jobs(job_title, area=area)
        linkedin_jobs = get_linkedin_jobs(job_title, job_location)

        context = {
            'headhunter_jobs': headhunter_jobs,
            'linkedin_jobs': linkedin_jobs,
        }
        return render(request, 'vacancy_lists.html', context)

    return render(request, 'parse_vacancy.html')


def get_headhunter_jobs(job_title, area=40):
    vacancies = []
    page = 0

    while True:
        data = get_page(job_title, area, page)
        js_obj = json.loads(data)

        for item in js_obj['items']:
            vacancies.append({
                'job_site': 'HeadHunter',
                'job_title': item['name'],
                'company_name': item['employer']['name'],
                'job_location': item['area']['name'],
                'job_url': item['alternate_url']
            })

        if (js_obj['pages'] - page) <= 1:
            break

        page += 1

    return vacancies


def get_page(position, area, page=0):
    params = {
        'text': f'NAME:{position}',
        'area': area,
        'page': page,
        'per_page': 100
    }

    req = requests.get('https://api.hh.ru/vacancies', params)
    data = req.content.decode()
    req.close()
    return data


def get_linkedin_jobs(keywords, location):
    base_url = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={}&location={}&start='
    keywords = keywords.replace(' ', '+')
    location = location.replace(' ', '+')

    start = 0
    linkedin_jobs = []
    while True:
        url = base_url.format(keywords, location) + str(start)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = soup.find_all('li')

        num_jobs_returned = len(jobs)

        if num_jobs_returned == 0:
            break

        for job in jobs:
            job_item = dict()
            job_item['job_title'] = job.find('h3').get_text(strip=True) if job.find('h3') else 'not-found'
            job_item['job_detail_url'] = job.find('a', {'class': 'base-card__full-link'})['href'] if job.find('a', {'class': 'base-card__full-link'}) else 'not-found'

            company = job.find('h4')
            if company and company.find('a'):
                job_item['company_name'] = company.find('a').get_text(strip=True)
            else:
                job_item['company_name'] = 'not-found'
            job_item['job_site'] = 'LinkedIn'
            company_location = job.find('span', {'class': 'job-search-card__location'}).get_text(
                strip=True) if job.find('span', {'class': 'job-search-card__location'}) else 'not-found'

            if company_location != 'not-found':
                job_item['company_location'] = company_location.split(',')[0]
            else:
                job_item['company_location'] = company_location
            linkedin_jobs.append(job_item)

        if len(linkedin_jobs) == 25:
            break

        start += 25

    return linkedin_jobs
