from django.http import HttpResponse
from django.shortcuts import render


def topic(request) -> HttpResponse:
    context = {
        'topics' : [
            {
                'title': 'Topic 1',
                'description': 'Content 1',
                'student': 'Student 1'},
            {
                'title': 'Topic 2',
                'description': 'Content 2',
                'student': 'Student 2'},
            {
                'title': 'Topic 3',
                'description': 'Content 3',
                'student': 'Student 3'},
            {
                'title': 'Topic 4',
                'description': 'Content 4',
                'student': 'Student 4'
            }
        ]
    }
    return render(request, "topic.html", context)
