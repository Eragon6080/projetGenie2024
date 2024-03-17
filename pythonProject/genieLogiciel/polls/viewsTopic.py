from django.http import HttpResponse
from django.shortcuts import render


def topic(request) -> HttpResponse:
    context = {
        'topics': {
            'topic': {
                "title": "Topic1",
                "description": "Description1",
                "student": "Matthys"
            },
            'topic1': {
                "title": "Topic2",
                "description": "Description2",
                "student": "Matthys"
            }
        }
    }
    return render(request, "topic.html", context)
