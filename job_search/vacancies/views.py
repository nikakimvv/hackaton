import requests
from django.shortcuts import render
from .forms import JobSearchForm
from .models import Vacancy
from .utils import *
import time

def job_search_view(request):
    if request.method == 'POST':
        form = JobSearchForm(request.POST)
        if form.is_valid():
            profession = form.cleaned_data['profession']
            salary = form.cleaned_data['salary']
            region = form.cleaned_data['region']

            url = "https://api.hh.ru/vacancies" 
            params = {
                'text': profession,
                'area': get_region_id(region),
                'salary': salary,
                'only_with_salary': True if salary else False,
                'per_page': 10,  # Ограничение на 10 вакансий
                'page': 0,       # Первая страница результатов
            }

            response = requests.get(url, params=params)
            if response.status_code == 200:
                vacancies_data = response.json().get('items', [])
            else:
                vacancies_data = []

            saved_vacancies = []
            for vacancy in vacancies_data:
                target_text = run_llm(vacancy['name'], profession)
                # print(vacancy['name'], profession)
                print(target_text)
                salary = vacancy.get('salary', {})
                if target_text == 'Да':
                    saved_vacancy = Vacancy.objects.create(
                        query=profession,
                        title=vacancy['name'],
                        salary_from=salary.get('from'),
                        salary_to=salary.get('to'),
                        currency=salary.get('currency'),
                        employer=vacancy['employer']['name'],
                        url=vacancy['alternate_url']
                    )
                    saved_vacancies.append(saved_vacancy)
                    export_to_csv()
                    time.sleep(0.1)

            return render(request, 'vacancies/job_search.html', {
                'form': form,
                'vacancies': saved_vacancies,
            })
    else:
        form = JobSearchForm()

    return render(request, 'vacancies/job_search.html', {'form': form})
