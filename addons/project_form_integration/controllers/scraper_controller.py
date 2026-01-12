from odoo import http
from odoo.http import request
import json
import logging

from ..services.zillow import scrape_zillow
from ..services.asce_hazard import scrape_asce_hazard

_logger = logging.getLogger(__name__)


class ScraperController(http.Controller):
    
    @http.route('/api/scrape/zillow', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def scrape_zillow_endpoint(self, **kwargs):
        """
        Scrape lot size and parcel number from Zillow using an address.
        
        Request body:
        {
            "address": "1745 SE 4101, ANDREWS, TX 79714-5998",
            "base_url": "https://www.zillow.com/homes/"  (Optional)
        }
        
        Response:
        {
            "status": "success",
            "data": {
                "lot_size": "1.50 Acres",
                "parcel_number": "1907174400000"
            }
        }
        """
        # Handle CORS preflight
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(
                json.dumps({'status': 'ok'}),
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                }
            )

        try:
            # Parse request data
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except:
                data = request.params

            address = data.get('address')
            base_url = data.get('base_url', "https://www.zillow.com/homes/")
            
            if not address:
                return request.make_response(
                    json.dumps({
                        'status': 'error',
                        'message': 'Missing required parameter: address'
                    }),
                    headers={
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    status=400
                )

            # Run the scraper function
            _logger.info("Scraping Zillow for address: %s", address)
            result = scrape_zillow(address, base_url)
            _logger.info("Scrape result: %s", result)

            return request.make_response(
                json.dumps({
                    'status': 'success',
                    'data': result
                }),
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                }
            )

        except Exception as e:
            _logger.error("Error scraping Zillow: %s", str(e))
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': str(e)
                }),
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                status=500
            )

    @http.route('/api/scrape/asce', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def scrape_asce_endpoint(self, **kwargs):
        """
        Scrape wind speed and snow load from ASCE Hazard Tool using an address.
        
        Request body:
        {
            "address": "615 N SHIRK RD, NEW HOLLAND, PA 17557",
            "standard": "ASCE/SEI 7-22",  (Optional, default: "ASCE/SEI 7-22")
            "risk_category": "II"  (Optional, default: "II")
        }
        
        Response:
        {
            "status": "success",
            "data": {
                "wind_speed": "113 mph",
                "snow_load": "54 lb/ft²"
            }
        }
        """
        # Handle CORS preflight
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(
                json.dumps({'status': 'ok'}),
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                }
            )

        try:
            # Parse request data
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except:
                data = request.params

            address = data.get('address')
            standard = data.get('standard', "ASCE/SEI 7-22")
            risk_category = data.get('risk_category', "II")
            
            if not address:
                return request.make_response(
                    json.dumps({
                        'status': 'error',
                        'message': 'Missing required parameter: address'
                    }),
                    headers={
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    status=400
                )

            # Run the ASCE scraper
            _logger.info("Scraping ASCE for address: %s", address)
            result = scrape_asce_hazard(address, standard, risk_category)
            _logger.info("ASCE scrape result: %s", result)

            return request.make_response(
                json.dumps({
                    'status': 'success',
                    'data': result
                }),
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                }
            )

        except Exception as e:
            _logger.error("Error scraping ASCE: %s", str(e))
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': str(e)
                }),
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                status=500
            )

    @http.route('/api/scrape/combined', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def scrape_combined_endpoint(self, **kwargs):
        """
        Scrape data from both Zillow and ASCE Hazard Tool using an address.
        
        Request body:
        {
            "address": "615 N SHIRK RD, NEW HOLLAND, PA 17557",
            "zillow_base_url": "https://www.zillow.com/homes/",  (Optional)
            "asce_standard": "ASCE/SEI 7-22",  (Optional)
            "asce_risk_category": "II"  (Optional)
        }
        
        Response:
        {
            "status": "success",
            "data": {
                "asce": {
                    "wind_speed": "113 mph",
                    "snow_load": "54 lb/ft²"
                },
                "zillow": {
                    "lot_size": "1.50 Acres",
                    "parcel_number": "1907174400000"
                }
            }
        }
        """
        # Handle CORS preflight
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(
                json.dumps({'status': 'ok'}),
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                }
            )

        try:
            # Parse request data
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except:
                data = request.params

            address = data.get('address')
            zillow_base_url = data.get('zillow_base_url', "https://www.zillow.com/homes/")
            asce_standard = data.get('asce_standard', "ASCE/SEI 7-22")
            asce_risk_category = data.get('asce_risk_category', "II")
            
            if not address:
                return request.make_response(
                    json.dumps({
                        'status': 'error',
                        'message': 'Missing required parameter: address'
                    }),
                    headers={
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    status=400
                )

            combined_result = {
                'asce': None,
                'zillow': None
            }
            errors = []

            # Scrape ASCE
            _logger.info("Scraping ASCE for address: %s", address)
            try:
                combined_result['asce'] = scrape_asce_hazard(address, asce_standard, asce_risk_category)
            except Exception as e:
                _logger.error("ASCE scraping failed: %s", str(e))
                errors.append(f"ASCE: {str(e)}")

            # Scrape Zillow
            _logger.info("Scraping Zillow for address: %s", address)
            try:
                combined_result['zillow'] = scrape_zillow(address, zillow_base_url)
            except Exception as e:
                _logger.error("Zillow scraping failed: %s", str(e))
                errors.append(f"Zillow: {str(e)}")

            _logger.info("Combined scrape result: %s", combined_result)

            response_data = {
                'status': 'success' if not errors else 'partial',
                'data': combined_result
            }
            
            if errors:
                response_data['errors'] = errors

            return request.make_response(
                json.dumps(response_data),
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                }
            )

        except Exception as e:
            _logger.error("Error in combined scrape: %s", str(e))
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': str(e)
                }),
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                status=500
            )
