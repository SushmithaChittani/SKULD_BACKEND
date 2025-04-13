from rest_framework import renderers
from rest_framework.utils import json
from django.utils.encoding import force_str
from rest_framework import status
from datetime import datetime

class CustomJSONRenderer(renderers.JSONRenderer):
    """
    Custom API response format renderer that wraps all responses in a consistent structure.
    Format:
    {
        "success": true/false,
        "timestamp": "ISO-8601 datetime",
        "data": {...},  # or [...] for lists
        "error": null,  # or {...} if error occurred
        "metadata": {...}  # pagination, etc.
    }
    """
    charset = 'utf-8'
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context['response'] if renderer_context else None
        response_data = {
            'success': status.is_success(response.status_code) if response else True,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'data': None,
            'error': None,
            'metadata': None
        }

        if response and status.is_client_error(response.status_code) or status.is_server_error(response.status_code):
            # Handle error responses
            response_data['error'] = self.format_error(data, response.status_code)
        else:
            # Handle successful responses
            if isinstance(data, dict):
                if 'results' in data and ('next' in data or 'previous' in data):
                    # Handle paginated responses
                    response_data['data'] = data.get('results', [])
                    response_data['metadata'] = {
                        'count': data.get('count', 0),
                        'next': data.get('next'),
                        'previous': data.get('previous')
                    }
                else:
                    # Standard dict response
                    response_data['data'] = data
            else:
                # List or other types
                response_data['data'] = data

        # Ensure we don't have null data when success is true
        if response_data['success'] and response_data['data'] is None:
            response_data['data'] = {}

        return json.dumps(response_data, ensure_ascii=False)

    def format_error(self, data, status_code):
        """
        Standardize error response format
        {
            "code": "error_code",
            "message": "Human-readable message",
            "details": {}  # additional error details
        }
        """
        if isinstance(data, dict):
            error_code = data.get('code', str(status_code))
            message = data.get('detail', data.get('message', 'An error occurred'))
            
            # Handle DRF validation errors
            if 'detail' not in data and 'non_field_errors' not in data:
                message = "Validation error"
            
            return {
                'code': error_code,
                'message': force_str(message),
                'details': {k: v for k, v in data.items() if k not in ['code', 'detail', 'message']}
            }
        return {
            'code': str(status_code),
            'message': force_str(data) if data else "An error occurred",
            'details': None
        }


class JPEGRenderer(renderers.BaseRenderer):
    """
    Renderer for JPEG image responses
    """
    media_type = 'image/jpeg'
    format = 'jpg'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


class PNGRenderer(renderers.BaseRenderer):
    """
    Renderer for PNG image responses
    """
    media_type = 'image/png'
    format = 'png'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


class PDFRenderer(renderers.BaseRenderer):
    """
    Renderer for PDF responses (e.g., workout plans export)
    """
    media_type = 'application/pdf'
    format = 'pdf'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


class CSVRenderer(renderers.BaseRenderer):
    """
    Renderer for CSV responses (e.g., progress data export)
    """
    media_type = 'text/csv'
    format = 'csv'
    charset = 'utf-8'
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


class BrowsableAPIRenderer(renderers.BrowsableAPIRenderer):
    """
    Customized browsable API renderer that maintains our response format
    """
    def get_content(self, renderer, data, accepted_media_type, renderer_context):
        # Let the original renderer handle the content
        content = super().get_content(renderer, data, accepted_media_type, renderer_context)
        
        # Only wrap if it's our custom JSON renderer
        if isinstance(renderer, CustomJSONRenderer):
            response = renderer_context['response']
            if status.is_success(response.status_code):
                return {
                    'success': True,
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'data': content,
                    'error': None,
                    'metadata': None
                }
            else:
                return {
                    'success': False,
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'data': None,
                    'error': content,
                    'metadata': None
                }
        return content