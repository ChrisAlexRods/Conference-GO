from django.http import JsonResponse
from .models import Conference, Location, State
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods
import json
import requests
from events.keys import PEXELS_KEY

# from events.keys import PEXELS_API_KEY


class LocationListEncoder(ModelEncoder):
    model = Location
    properties = ["name"]


class ConferenceDetailEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
        "description",
        "max_presentations",
        "max_attendees",
        "image_url",
        "starts",
        "ends",
        "created",
        "updated",
        "location",
    ]
    encoders = {
        "location": LocationListEncoder(),
    }


class LocationDetailEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "city",
        "room_count",
        "created",
        "updated",
        "image_url",
    ]


def conference_to_dict(conference):
    return {
        "name": conference.name,
        "starts": conference.starts,
        "ends": conference.ends,
        "description": conference.description,
        "created": conference.created,
        "updated": conference.updated,
        "max_presentations": conference.max_presentations,
        "max_attendees": conference.max_attendees,
        "location": {
            "name": conference.location.name,
            "href": conference.location.get_api_url(),
        },
    }


class ConferenceListEncoder(ModelEncoder):
    model = Conference
    properties = ["name"]


@require_http_methods(["GET", "POST"])
def api_list_conferences(request):
    if request.method == "GET":
        conferences = Conference.objects.all()
        return JsonResponse(
            {"conferences": conferences},
            encoder=ConferenceListEncoder,
        )
    # POST
    else:
        content = json.loads(request.body)

        try:
            location = Location.objects.get(id=content["location"])
            content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid State Abbreviation "},
            )

    conference = Conference.objects.create(**content)
    return JsonResponse(
        conference,
        encoder=ConferenceDetailEncoder,
        safe=False,
    )
    # response = []
    # conferences = Conference.objects.all()
    # for conference in conferences:
    #    response.append(
    #        {
    #            "name": conference.name,
    #           "href": conference.get_api_url(),
    #        }
    #    )
    # return JsonResponse({"conferences": response})


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_conference(request, id):
    if request.method == "GET":
        conference = Conference.objects.get(id=id)
        return JsonResponse(
            conference,
            encoder=ConferenceDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Conference.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    # PUT
    else:
        content = json.loads(request.body)

        Conference.objects.filter(id=id).update(**content)

        conference = Conference.objects.get(id=id)
        return JsonResponse(
            conference,
            encoder=ConferenceDetailEncoder,
            safe=False,
        )


# GET AND POST
@require_http_methods(["GET", "POST"])
def api_list_locations(request):
    # I NEED HELP UDNERSTANDING THIS
    if request.method == "GET":
        locations = Location.objects.all()
        return JsonResponse(
            {"locations": locations},
            encoder=LocationListEncoder,
        )
    else:
        content = json.loads(request.body)
        # Make a request to pexeles passing in the city and state
        # Clean that data for the image
        # Add that image to my location model
        URL = f'https://api.pexels.com/v1/search?query={content["city"]}+{content["state"]}'
        headers = {"Authorization": PEXELS_KEY}

        resp = requests.get(URL, headers=headers)
        data = resp.json()
        print(URL)
        content["image_url"] = data["photos"][0]["src"]["original"]

        # WE'RE abbreviating state to make it JSON Readable. Don't udnerstand code below
        try:
            state = State.objects.get(abbreviation=content["state"])
            content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid State Abbreviation "},
                status=400,
            )
        # Above me made a try and except statement to catch potnetial erros
        # Need explination
        location = Location.objects.create(**content)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )


def get_extra_data(self, o):
    return {"state": o.state.abbreviation}


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_location(request, id):
    # GET
    if request.method == "GET":
        location = Location.objects.get(id=id)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )
    # DELETE
    elif request.method == "DELETE":
        count, _ = Location.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    # PUT
    else:
        # copied from create
        content = json.loads(request.body)

        try:
            # new code
            if "state" in content:
                state = State.objects.get(abbreviation=content["state"])
                content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
            )

        # new code
        Location.objects.filter(id=id).update(**content)

        # copied from get detail
        location = Location.objects.get(id=id)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )

    # location = Location.objects.get(id=id)
    # return JsonResponse(
    #    {
    #        "name": location.name,
    #        "city": location.city,
    #        "room_count": location.room_count,
    #        "created": location.created,
    #        "updated": location.updated,
    #        "state": location.state.abbreviation,
    #    }
    # )
