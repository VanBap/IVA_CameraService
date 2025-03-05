import logging
import requests
from api import settings
from common.enums import EventType

logger = logging.getLogger('app')


def watchlist_post(url, json_payload):
    headers = {
        'Content-Type': 'application/json',
        'Api-Key': settings.API_KEY_WATCHLIST_SERVICE
    }
    return requests.post(url, json=json_payload, headers=headers)


def watchlist_get(url):
    headers = {
        'Content-Type': 'application/json',
        'Api-Key': settings.API_KEY_WATCHLIST_SERVICE
    }
    return requests.get(url, headers=headers)


def get_json_response(res):
    if res.status_code != 200:
        logger.error('Watchlist service error code {}'.format(res.status_code))
        return None
    return res.json()


def convert_dict_key_str_to_int(dict_data):
    results = {}
    for key, value in dict_data.items():
        results[int(key)] = value
    return results


class BaseWatchlistUtil:
    API_GET_DOSSIER = ''
    API_GET_DOSSIER_ITEM = ''
    API_GET_BULK_DOSSIERS = ''
    API_GET_BULK_WATCHLISTS = ''

    @classmethod
    def get_dossier(cls, dossier_id):
        if not dossier_id:
            return None

        url = cls.API_GET_DOSSIER + str(dossier_id)

        try:
            res = watchlist_get(url)
            return get_json_response(res)
        except Exception as ex:
            logger.exception(ex)
            return None

    @classmethod
    def get_dossier_item(cls, dossier_item_id):
        if not dossier_item_id:
            return None

        url = cls.API_GET_DOSSIER_ITEM + str(dossier_item_id)

        try:
            res = watchlist_get(url)
            return get_json_response(res)

        except Exception as ex:
            logger.exception(ex)
            return None

    @classmethod
    def get_bulk_dossiers(cls, dossier_ids, return_mode='only-watchlist'):
        """
        return dict of dossier info {dossier_id -> dossier_info}
        dossier_id: int
        dossier_info: {id, name, detected_class_id, [list of watchlists] }
        """
        if not dossier_ids:
            return {}

        # query watchlist services
        url = cls.API_GET_BULK_DOSSIERS
        payload = {
            'dossiers': dossier_ids,
            'return_mode': return_mode
        }
        try:
            res = watchlist_post(url, payload)
            dict_dossiers = get_json_response(res) or {}  # key is string
            # IMPORTANT: response dossier_id is string, need converting to int
            return convert_dict_key_str_to_int(dict_dossiers)

        except Exception as ex:
            logger.exception(ex)
            return {}

    @classmethod
    def get_bulk_watchlists(cls, watchlist_ids, return_mode=''):
        """
        return dict of watchlist info {watchlist_id -> watchlist_info}
        watchlist_id: int
        watchlist_info: {id, name, color,... }
        """
        if not watchlist_ids:
            return {}

        # query watchlist services
        url = cls.API_GET_BULK_WATCHLISTS
        payload = {
            'watchlists': watchlist_ids
        }
        if return_mode:
            payload['return_mode'] = return_mode
        try:
            res = watchlist_post(url, payload)
            dict_results = get_json_response(res) or {}
            return convert_dict_key_str_to_int(dict_results)
        except Exception as ex:
            logger.exception(ex)
            return {}


class FaceWatchlistUtil(BaseWatchlistUtil):
    API_GET_DOSSIER = settings.API_GET_FACE_DOSSIER
    API_GET_DOSSIER_ITEM = settings.API_GET_FACE_DOSSIER_ITEM
    API_GET_BULK_DOSSIERS = settings.API_GET_BULK_FACE_DOSSIERS
    API_GET_BULK_WATCHLISTS = settings.API_GET_BULK_FACE_WATCHLISTS


class HumanWatchlistUtil(BaseWatchlistUtil):
    API_GET_DOSSIER = settings.API_GET_HUMAN_DOSSIER
    API_GET_DOSSIER_ITEM = settings.API_GET_HUMAN_DOSSIER_ITEM
    API_GET_BULK_DOSSIERS = settings.API_GET_BULK_HUMAN_DOSSIERS
    API_GET_BULK_WATCHLISTS = settings.API_GET_BULK_HUMAN_WATCHLISTS


class VehicleWatchlistUtil(BaseWatchlistUtil):
    API_GET_DOSSIER = settings.API_GET_VEHICLE_DOSSIER
    API_GET_DOSSIER_ITEM = settings.API_GET_VEHICLE_DOSSIER_ITEM
    API_GET_BULK_DOSSIERS = settings.API_GET_BULK_VEHICLE_DOSSIERS
    API_GET_BULK_WATCHLISTS = settings.API_GET_BULK_VEHICLE_WATCHLISTS


class LicensePlateWatchlistUtil(BaseWatchlistUtil):
    API_GET_BULK_WATCHLISTS = settings.API_GET_BULK_PLATE_WATCHLISTS

    @classmethod
    def get_dossier(cls, plate_id=None, plate_text=None):
        if (not plate_id) and (not plate_text):
            return None

        url = ''
        if plate_id:
            url = settings.API_GET_PLATE + str(plate_id)
        elif plate_text:
            url = settings.API_GET_PLATE + f'name/{plate_text}'

        try:
            res = watchlist_get(url)
            return get_json_response(res)
        except Exception as ex:
            logger.exception(ex)
            return None

    @classmethod
    def get_bulk_dossiers(cls, list_plate_texts, return_mode='only-watchlist'):
        """
        return dict of plate info
        {
            '29A1234' : {
                'watchlists': [list of watchlists]
            },
        }
        """
        if not list_plate_texts:
            return {}

        # query watchlist services
        url = settings.API_GET_BULK_PLATES
        payload = {
            'plate_names': list_plate_texts
        }
        try:
            res = watchlist_post(url, payload)
            return get_json_response(res) or {}
        except Exception as ex:
            logger.exception(ex)
            return {}


def get_all_plate_city():
    """
    Return:
    [
        {
            "id": 1,
            "code": "67",
            "city": {
                "id": 1,
                "name": "An Giang",
                "zip_code": null
            }
        },
    ]
    """
    url = settings.WATCHLIST_SERVICE + '/api/plate/plates/config/plate-codes/filter'
    try:
        res = watchlist_post(url, {'return_mode': 'all'})
        return get_json_response(res)
    except Exception as ex:
        logger.exception(ex)


MAP_WATCHLIST_CLASSES = {
    EventType.FACE: FaceWatchlistUtil,
    EventType.HUMAN: HumanWatchlistUtil,
    EventType.VEHICLE: VehicleWatchlistUtil,
    EventType.LICENSE_PLATE: LicensePlateWatchlistUtil
}


def get_watchlist_util_class(dossier_type):
    return MAP_WATCHLIST_CLASSES.get(dossier_type)
