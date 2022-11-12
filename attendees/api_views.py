from django.http import JsonResponse
from common.json import ModelEncoder
from .models import Attendee
from django.views.decorators.http import require_http_methods
import json
from events.models import Conference


class AttendeListEncoder(ModelEncoder):
    model = Attendee
    properties = ["name"]


class ConferenceListEncoder(ModelEncoder):
    model = Conference
    properties = ["name"]


class AttendeDetailEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",
        "conference",
    ]
    encoders = {
        "conference": ConferenceListEncoder(),
    }


@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_id):
    """
    Lists the attendees names and the link to the attendee
    for the specified conference id.

    Returns a dictionary with a single key "attendees" which
    is a list of attendee names and URLS. Each entry in the list
    is a dictionary that contains the name of the attendee and
    the link to the attendee's information.

    {
        "attendees": [
            {
                "name": attendee's name,
                "href": URL to the attendee,
            },
            ...
        ]
    }
    """
    if request.method == "GET":
        attendees = Attendee.objects.filter(conference=conference_id)
        return JsonResponse(
            {"attendees": attendees},
            encoder=AttendeListEncoder,
        )
    else:
        content = json.loads(request.body)
        try:
            conference = Conference.objects.get(id=conference_id)
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )

        attendee = Attendee.objects.create(**content)
        return JsonResponse(attendee, encoder=AttendeDetailEncoder, safe=False)


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_attendee(request, id):
    if request.method == "GET":
        person = Attendee.objects.get(id=id)
        return JsonResponse(
            person,
            encoder=AttendeDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Attendee.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    # PUT
    else:
        content = json.loads(request.body)

        Attendee.objects.filter(id=id).update(**content)

        person = Attendee.objects.get(id=id)
        return JsonResponse(
            person,
            encoder=AttendeDetailEncoder,
            safe=False,
        )
