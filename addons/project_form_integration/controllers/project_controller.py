from odoo import http
from odoo.http import request
import json
import re
import logging

_logger = logging.getLogger(__name__)

class ProjectController(http.Controller):


    @http.route('/api/create-project', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def create_project(self, **kwargs):
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
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.info("Data: %s", data)
        except:
            data = request.params
        
        user_profile_data = data.get('user_profile', {})
        project_data = data.get('project', {})
        services_data = data.get('services', [])
        system_summary_data = data.get('system_summary', {})
        battery_info_data = data.get('battery_info', {})
        site_details_data = data.get('site_details', {})
        electrical_details_data = data.get('electrical_details', {})
        advanced_electrical_details_data = data.get('advanced_electrical_details', {})
        optional_extra_details_data = data.get('optional_extra_details', {})
        system_components_data = data.get('system_components', [])
        uploads_data = data.get('uploads', [])
        engineering_firm_data = data.get('engineering_firm', {})

        # 1. User Profile
        user_profile = request.env['project.form.user.profile'].sudo().search([
            ('email', '=', user_profile_data.get('email'))
        ], limit=1)
        
        if not user_profile:
            user_profile = request.env['project.form.user.profile'].sudo().create({
                'company_name': user_profile_data.get('company_name'),
                'contact_name': user_profile_data.get('contact_name'),
                'email': user_profile_data.get('email'),
                'phone': user_profile_data.get('phone'),
            })

        # 2. Submission Type
        submission_type_id = None
        if project_data.get('submission_type_id'):
            _logger.info("Validating submission_type_id: %s", project_data.get('submission_type_id'))
            # Search by UUID
            submission_type = request.env['project.form.submission.type'].sudo().search([('uuid', '=', project_data.get('submission_type_id'))], limit=1)
            if submission_type:
                submission_type_id = submission_type.uuid
                _logger.info("Submission type found: %s (UUID: %s)", submission_type.name, submission_type_id)
            else:
                _logger.error("Submission type ID %s does not exist", project_data.get('submission_type_id'))
                error_response = json.dumps({
                    'status': 'error',
                    'message': f"Submission type with ID {project_data.get('submission_type_id')} does not exist",
                    'details': 'Please provide a valid submission_type_id or submission_type_name'
                })
                return request.make_response(
                    error_response,
                    headers={
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    status=400
                )
        elif project_data.get('submission_type_name'):
            _logger.info("Searching for submission_type_name: %s", project_data.get('submission_type_name'))
            submission_type = request.env['project.form.submission.type'].sudo().search([
                ('name', '=', project_data.get('submission_type_name'))
            ], limit=1)
            if submission_type:
                submission_type_id = submission_type.uuid
                _logger.info("Submission type found: %s (UUID: %s)", submission_type.name, submission_type_id)
            else:
                _logger.error("Submission type name '%s' does not exist", project_data.get('submission_type_name'))
                error_response = json.dumps({
                    'status': 'error',
                    'message': f"Submission type with name '{project_data.get('submission_type_name')}' does not exist",
                    'details': 'Please provide a valid submission_type_id or submission_type_name'
                })
                return request.make_response(
                    error_response,
                    headers={
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    status=400
                )

        # 3. Services
        service_ids = []
        for service_data in services_data:
            if isinstance(service_data, str):
                # Check if it looks like a UUID (contains hyphens and is 36 chars)
                if '-' in service_data and len(service_data) == 36:
                    # Treat as UUID
                    service_ids.append(service_data)
                else:
                    # Treat as service name and lookup
                    service = request.env['project.form.service'].sudo().search([
                        ('name', '=', service_data)
                    ], limit=1)
                    if service:
                        service_ids.append(service.uuid)
                    else:
                        _logger.warning("Service with name '%s' not found", service_data)
            elif isinstance(service_data, dict):
                # Dict with 'id' or 'name'
                uuid_val = service_data.get('id') or service_data.get('uuid')
                if uuid_val:
                    service_ids.append(uuid_val)
                else:
                    service = request.env['project.form.service'].sudo().search([
                        ('name', '=', service_data.get('name'))
                    ], limit=1)
                    if service:
                        service_ids.append(service.uuid)
                    else:
                        _logger.warning("Service with name '%s' not found", service_data.get('name'))

        try:
            # 4. Create Project
            # Resolve service UUIDs to Integer IDs for the Many2many write
            service_int_ids = []
            if service_ids:
                services = request.env['project.form.service'].sudo().search([('uuid', 'in', service_ids)])
                service_int_ids = services.ids

            project = request.env['project.form.project'].sudo().create({
                'name': project_data.get('name'),
                'user_profile_id': user_profile.uuid,
                'address': project_data.get('address'),
                'type': project_data.get('type'),
                'submission_type_id': submission_type_id,
                'general_notes': project_data.get('general_notes'),
                'service_ids': [(6, 0, service_int_ids)] if service_int_ids else False,
            })
        except Exception as e:
            _logger.exception("Failed to create project")
            error_response = json.dumps({
                'status': 'error',
                'message': str(e),
                'details': 'Failed to create project. Please check the logs for more details.'
            })
            return request.make_response(
                error_response,
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                status=422
            )

        # 5. Related Models
        system_summary_id = None
        battery_info_id = None
        try:
            if system_summary_data:
                _logger.info("Creating system summary with data: %s", system_summary_data)
                system_summary = request.env['project.form.system.summary'].sudo().create({
                    'project_id': project.uuid,
                    'system_size': system_summary_data.get('system_size'),
                    'system_type': system_summary_data.get('system_type'),
                    'pv_modules': system_summary_data.get('pv_modules'),
                    'inverters': system_summary_data.get('inverters'),
                })
                system_summary_id = system_summary.uuid
                _logger.info("System summary created with ID: %s", system_summary_id)

                if battery_info_data:
                    _logger.info("Creating battery info with data: %s", battery_info_data)
                    image_urls = battery_info_data.get('image', [])
                    if isinstance(image_urls, list):
                        image_urls = json.dumps(image_urls)
                    
                    battery_info = request.env['project.form.battery.info'].sudo().create({
                        'system_summary_id': system_summary.uuid,
                        'qty': battery_info_data.get('qty'),
                        'model': battery_info_data.get('model'),
                        'image': image_urls,
                    })
                    battery_info_id = battery_info.uuid
                    _logger.info("Battery info created with ID: %s", battery_info_id)
        except Exception as e:
            _logger.exception("Failed to create system summary or battery info: %s", str(e))

        site_details_id = None
        try:
            if site_details_data:
                _logger.info("Creating site details with data: %s", site_details_data)
                site_details = request.env['project.form.site.detail'].sudo().create({
                    'project_id': project.uuid,
                    'roof_material': site_details_data.get('roof_material'),
                    'roof_pitch': site_details_data.get('roof_pitch'),
                    'number_of_arrays': site_details_data.get('number_of_arrays'),
                    'ground_mount_type': site_details_data.get('ground_mount_type'),
                    'foundation_type': site_details_data.get('foundation_type'),
                    'main_panel_size': site_details_data.get('main_panel_size'),
                    'utility_provider': site_details_data.get('utility_provider'),
                    'jurisdiction': site_details_data.get('jurisdiction'),
                })
                site_details_id = site_details.uuid
                _logger.info("Site details created with ID: %s", site_details_id)
        except Exception as e:
            _logger.exception("Failed to create site details: %s", str(e))

        electrical_details_id = None
        try:
            if electrical_details_data:
                _logger.info("Creating electrical details with data: %s", electrical_details_data)
                one_line_diagram = electrical_details_data.get('one_line_diagram', [])
                if isinstance(one_line_diagram, list):
                    one_line_diagram = json.dumps(one_line_diagram)
                
                electrical_details = request.env['project.form.electrical.detail'].sudo().create({
                    'project_id': project.uuid,
                    'main_panel_size': electrical_details_data.get('main_panel_size'),
                    'bus_rating': electrical_details_data.get('bus_rating'),
                    'main_breaker': electrical_details_data.get('main_breaker'),
                    'pv_breaker_location': electrical_details_data.get('pv_breaker_location'),
                    'one_line_diagram': one_line_diagram,
                })
                electrical_details_id = electrical_details.uuid
                _logger.info("Electrical details created with ID: %s", electrical_details_id)
        except Exception as e:
            _logger.exception("Failed to create electrical details: %s", str(e))

        advanced_electrical_details_id = None
        try:
            if advanced_electrical_details_data:
                _logger.info("Creating advanced electrical details with data: %s", advanced_electrical_details_data)
                advanced_electrical_details = request.env['project.form.advanced.electrical.detail'].sudo().create({
                    'project_id': project.uuid,
                    'meter_location': advanced_electrical_details_data.get('meter_location'),
                    'service_entrance_type': advanced_electrical_details_data.get('service_entrance_type'),
                    'subpanel_details': advanced_electrical_details_data.get('subpanel_details'),
                })
                advanced_electrical_details_id = advanced_electrical_details.uuid
                _logger.info("Advanced electrical details created with ID: %s", advanced_electrical_details_id)
        except Exception as e:
            _logger.exception("Failed to create advanced electrical details: %s", str(e))

        optional_extra_details_id = None
        try:
            if optional_extra_details_data:
                _logger.info("Creating optional extra details with data: %s", optional_extra_details_data)
                optional_extra_details = request.env['project.form.optional.extra.detail'].sudo().create({
                    'project_id': project.uuid,
                    'miracle_watt_required': optional_extra_details_data.get('miracle_watt_required', False),
                    'miracle_watt_notes': optional_extra_details_data.get('miracle_watt_notes'),
                    'der_rlc_required': optional_extra_details_data.get('der_rlc_required', False),
                    'der_rlc_notes': optional_extra_details_data.get('der_rlc_notes'),
                    'setback_constraints': optional_extra_details_data.get('setback_constraints', False),
                    'setback_notes': optional_extra_details_data.get('setback_notes'),
                    'site_access_restrictions': optional_extra_details_data.get('site_access_restrictions', False),
                    'site_access_notes': optional_extra_details_data.get('site_access_notes'),
                    'inspection_notes': optional_extra_details_data.get('inspection_notes', False),
                    'inspection_notes_text': optional_extra_details_data.get('inspection_notes_text'),
                    'battery_sld_requested': optional_extra_details_data.get('battery_sld_requested', False),
                    'battery_sld_notes': optional_extra_details_data.get('battery_sld_notes'),
                })
                optional_extra_details_id = optional_extra_details.uuid
                _logger.info("Optional extra details created with ID: %s", optional_extra_details_id)
        except Exception as e:
            _logger.exception("Failed to create optional extra details: %s", str(e))

        system_component_ids = []
        try:
            for component_data in system_components_data:
                _logger.info("Creating system component with data: %s", component_data)
                attachment_urls = component_data.get('attachment', [])
                if isinstance(attachment_urls, list):
                    attachment_urls = json.dumps(attachment_urls)
                
                component = request.env['project.form.system.component'].sudo().create({
                    'project_id': project.uuid,
                    'type': component_data.get('type'),
                    'make_model': component_data.get('make_model'),
                    'qty': component_data.get('qty'),
                    'attachment': attachment_urls,
                    'notes': component_data.get('notes'),
                })
                system_component_ids.append(component.uuid)
                _logger.info("System component created with ID: %s", component.uuid)
        except Exception as e:
            _logger.exception("Failed to create system components: %s", str(e))

        upload_ids = []
        try:
            for upload_data in uploads_data:
                _logger.info("Creating upload with data: %s", upload_data)
                upload = request.env['project.form.upload'].sudo().create({
                    'project_id': project.uuid,
                    'url': upload_data.get('url'),
                    'name': upload_data.get('name'),
                    'category': upload_data.get('category'),
                    'mime_type': upload_data.get('mime_type'),
                    'size': upload_data.get('size'),
                })
                upload_ids.append(upload.uuid)
                _logger.info("Upload created with ID: %s", upload.uuid)
        except Exception as e:
            _logger.exception("Failed to create uploads: %s", str(e))

        # Create Odoo Task in Project Module
        odoo_task_id = None
        try:
            # Find or create default Odoo project for form submissions
            odoo_project = request.env['project.project'].sudo().search([
                ('name', '=', 'Form Submissions')
            ], limit=1)
            
            if not odoo_project:
                _logger.info("Creating 'Form Submissions' project in Odoo")
                odoo_project = request.env['project.project'].sudo().create({
                    'name': 'Form Submissions',
                    'description': 'Auto-generated tasks from project form API submissions'
                })
            
            # ===== 1. PREPARE TAGS FROM EXISTING DATA =====
            tag_ids = []
            tag_names = []
            
            # Add project type as tag
            if project.type:
                tag_names.append(project.type.capitalize())
            
            # Add submission type as tag
            if submission_type:
                tag_names.append(submission_type.name)
            
            # Add service names as tags
            if service_ids:
                services = request.env['project.form.service'].sudo().search([('uuid', 'in', service_ids)])
                for service in services:
                    tag_names.append(service.name)
            
            # Add system type as tag
            if system_summary_id:
                sys_sum = request.env['project.form.system.summary'].sudo().search([('uuid', '=', system_summary_id)], limit=1)
                if sys_sum and sys_sum.system_type:
                    tag_names.append(sys_sum.system_type.capitalize())
            
            # Create or find tags
            for tag_name in tag_names:
                tag = request.env['project.tags'].sudo().search([('name', '=', tag_name)], limit=1)
                if not tag:
                    tag = request.env['project.tags'].sudo().create({'name': tag_name})
                tag_ids.append(tag.id)
            
            _logger.info("Created/found tags: %s", tag_names)
            
            # ===== 2. CALCULATE SMART PRIORITY =====
            priority = '0'  # Default: Normal
            
            if system_summary_id:
                sys_sum = request.env['project.form.system.summary'].sudo().search([('uuid', '=', system_summary_id)], limit=1)
                if sys_sum and sys_sum.system_size:
                    if sys_sum.system_size > 20:
                        priority = '2'  # Very High
                    elif sys_sum.system_size >= 10:
                        priority = '1'  # High
            
            # Lower priority if critical data is missing
            if not electrical_details_id or not site_details_id:
                if priority == '2':
                    priority = '1'
                elif priority == '1':
                    priority = '0'
            
            _logger.info("Calculated priority: %s", priority)
            
            # ===== 3. BUILD RICH HTML DESCRIPTION =====
            html_description = f"""
<div style="font-family: Arial, sans-serif; font-size: 14px;">
    <h2 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;">
        🏗️ {project.name}
    </h2>
    
    <div style="background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="color: #2980b9; margin-top: 0;">📋 Project Details</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; font-weight: bold; width: 30%;">Address:</td>
                <td style="padding: 8px;">{project.address}</td>
            </tr>
            <tr style="background-color: #fff;">
                <td style="padding: 8px; font-weight: bold;">Type:</td>
                <td style="padding: 8px;"><span style="background-color: #3498db; color: white; padding: 3px 10px; border-radius: 3px;">{project.type.upper()}</span></td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Submission Type:</td>
                <td style="padding: 8px;">{submission_type.name if submission_type else 'N/A'}</td>
            </tr>
            <tr style="background-color: #fff;">
                <td style="padding: 8px; font-weight: bold;">General Notes:</td>
                <td style="padding: 8px;"><em>{project.general_notes or 'None'}</em></td>
            </tr>
        </table>
    </div>
    
    <div style="background-color: #e8f5e9; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="color: #27ae60; margin-top: 0;">👤 Customer Information</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; font-weight: bold; width: 30%;">Company:</td>
                <td style="padding: 8px;">{user_profile.company_name}</td>
            </tr>
            <tr style="background-color: #fff;">
                <td style="padding: 8px; font-weight: bold;">Contact:</td>
                <td style="padding: 8px;">{user_profile.contact_name}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Email:</td>
                <td style="padding: 8px;"><a href="mailto:{user_profile.email}">{user_profile.email}</a></td>
            </tr>
            <tr style="background-color: #fff;">
                <td style="padding: 8px; font-weight: bold;">Phone:</td>
                <td style="padding: 8px;">{user_profile.phone}</td>
            </tr>
        </table>
    </div>
    
    <div style="background-color: #fff3e0; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="color: #f39c12; margin-top: 0;">🔧 Services Requested</h3>
        <ul style="list-style-type: none; padding-left: 0;">
"""
            
            if service_ids:
                services = request.env['project.form.service'].sudo().search([('uuid', 'in', service_ids)])
                for service in services:
                    html_description += f'<li style="padding: 5px 0;">✓ <strong>{service.name}</strong></li>'
            else:
                html_description += '<li style="padding: 5px 0;"><em>No services specified</em></li>'
            
            html_description += """
        </ul>
    </div>
"""
            
            # System Summary Section
            if system_summary_id:
                sys_sum = request.env['project.form.system.summary'].sudo().search([('uuid', '=', system_summary_id)], limit=1)
                if sys_sum:
                    html_description += f"""
    <div style="background-color: #fce4ec; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="color: #e91e63; margin-top: 0;">⚡ System Summary</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; font-weight: bold; width: 30%;">System Size:</td>
                <td style="padding: 8px;"><strong style="color: #e91e63; font-size: 16px;">{sys_sum.system_size} kW</strong></td>
            </tr>
            <tr style="background-color: #fff;">
                <td style="padding: 8px; font-weight: bold;">System Type:</td>
                <td style="padding: 8px;">{sys_sum.system_type or 'N/A'}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">PV Modules:</td>
                <td style="padding: 8px;">{sys_sum.pv_modules or 'N/A'}</td>
            </tr>
            <tr style="background-color: #fff;">
                <td style="padding: 8px; font-weight: bold;">Inverters:</td>
                <td style="padding: 8px;">{sys_sum.inverters or 'N/A'}</td>
            </tr>
        </table>
"""
                    
                    # Battery Info
                    if battery_info_id:
                        batt = request.env['project.form.battery.info'].sudo().search([('uuid', '=', battery_info_id)], limit=1)
                        if batt:
                            html_description += f"""
        <div style="margin-top: 15px; padding: 10px; background-color: #fff; border-left: 4px solid #9c27b0;">
            <strong style="color: #9c27b0;">🔋 Battery:</strong> {batt.qty}x {batt.model}
        </div>
"""
                    
                    html_description += """
    </div>
"""
            
            # Site Details Section
            if site_details_id:
                site = request.env['project.form.site.detail'].sudo().search([('uuid', '=', site_details_id)], limit=1)
                if site:
                    html_description += f"""
    <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="color: #1976d2; margin-top: 0;">🏠 Site Details</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; font-weight: bold; width: 30%;">Roof Material:</td>
                <td style="padding: 8px;">{site.roof_material or 'N/A'}</td>
            </tr>
            <tr style="background-color: #fff;">
                <td style="padding: 8px; font-weight: bold;">Roof Pitch:</td>
                <td style="padding: 8px;">{site.roof_pitch or 'N/A'}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Number of Arrays:</td>
                <td style="padding: 8px;">{site.number_of_arrays or 0}</td>
            </tr>
            <tr style="background-color: #fff;">
                <td style="padding: 8px; font-weight: bold;">Utility Provider:</td>
                <td style="padding: 8px;">{site.utility_provider or 'N/A'}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Jurisdiction:</td>
                <td style="padding: 8px;">{site.jurisdiction or 'N/A'}</td>
            </tr>
        </table>
    </div>
"""
            
            # Electrical Details Section
            if electrical_details_id:
                elec = request.env['project.form.electrical.detail'].sudo().search([('uuid', '=', electrical_details_id)], limit=1)
                if elec:
                    html_description += f"""
    <div style="background-color: #fff9c4; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="color: #f57c00; margin-top: 0;">⚙️ Electrical Details</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; font-weight: bold; width: 30%;">Main Panel Size:</td>
                <td style="padding: 8px;">{elec.main_panel_size or 'N/A'}</td>
            </tr>
            <tr style="background-color: #fff;">
                <td style="padding: 8px; font-weight: bold;">Bus Rating:</td>
                <td style="padding: 8px;">{elec.bus_rating or 'N/A'}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Main Breaker:</td>
                <td style="padding: 8px;">{elec.main_breaker or 'N/A'}</td>
            </tr>
            <tr style="background-color: #fff;">
                <td style="padding: 8px; font-weight: bold;">PV Breaker Location:</td>
                <td style="padding: 8px;">{elec.pv_breaker_location or 'N/A'}</td>
            </tr>
        </table>
    </div>
"""
            
            # Advanced Electrical Details Section
            if advanced_electrical_details_id:
                adv_elec = request.env['project.form.advanced.electrical.detail'].sudo().search([('uuid', '=', advanced_electrical_details_id)], limit=1)
                if adv_elec:
                    html_description += f"""
    <div style="background-color: #f3e5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="color: #7b1fa2; margin-top: 0;">🔌 Advanced Electrical Details</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; font-weight: bold; width: 30%;">Meter Location:</td>
                <td style="padding: 8px;">{adv_elec.meter_location or 'N/A'}</td>
            </tr>
            <tr style="background-color: #fff;">
                <td style="padding: 8px; font-weight: bold;">Service Entrance Type:</td>
                <td style="padding: 8px;">{adv_elec.service_entrance_type or 'N/A'}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Subpanel Details:</td>
                <td style="padding: 8px;">{adv_elec.subpanel_details or 'N/A'}</td>
            </tr>
        </table>
    </div>
"""
            
            # Optional Extra Details Section
            if optional_extra_details_id:
                opt_extra = request.env['project.form.optional.extra.detail'].sudo().search([('uuid', '=', optional_extra_details_id)], limit=1)
                if opt_extra:
                    extras_list = []
                    if opt_extra.miracle_watt_required:
                        extras_list.append(f"<li>✓ <strong>Miracle Watt Required:</strong> {opt_extra.miracle_watt_notes or 'Yes'}</li>")
                    if opt_extra.der_rlc_required:
                        extras_list.append(f"<li>✓ <strong>DER RLC Required:</strong> {opt_extra.der_rlc_notes or 'Yes'}</li>")
                    if opt_extra.setback_constraints:
                        extras_list.append(f"<li>⚠️ <strong>Setback Constraints:</strong> {opt_extra.setback_notes or 'Yes'}</li>")
                    if opt_extra.site_access_restrictions:
                        extras_list.append(f"<li>⚠️ <strong>Site Access Restrictions:</strong> {opt_extra.site_access_notes or 'Yes'}</li>")
                    if opt_extra.inspection_notes:
                        extras_list.append(f"<li>📝 <strong>Inspection Notes:</strong> {opt_extra.inspection_notes_text or 'Yes'}</li>")
                    if opt_extra.battery_sld_requested:
                        extras_list.append(f"<li>✓ <strong>Battery SLD Requested:</strong> {opt_extra.battery_sld_notes or 'Yes'}</li>")
                    
                    if extras_list:
                        html_description += f"""
    <div style="background-color: #ffe0b2; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="color: #e65100; margin-top: 0;">📌 Optional Extra Details</h3>
        <ul style="list-style-type: none; padding-left: 0;">
            {''.join(extras_list)}
        </ul>
    </div>
"""
            
            # System Components Section
            if system_component_ids:
                html_description += f"""
    <div style="background-color: #e0f2f1; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="color: #00695c; margin-top: 0;">🔩 System Components ({len(system_component_ids)})</h3>
        <table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">
            <thead>
                <tr style="background-color: #00695c; color: white;">
                    <th style="padding: 10px; text-align: left;">Type</th>
                    <th style="padding: 10px; text-align: left;">Make/Model</th>
                    <th style="padding: 10px; text-align: center;">Qty</th>
                    <th style="padding: 10px; text-align: left;">Notes</th>
                </tr>
            </thead>
            <tbody>
"""
                
                for comp_uuid in system_component_ids:
                    comp = request.env['project.form.system.component'].sudo().search([('uuid', '=', comp_uuid)], limit=1)
                    if comp:
                        html_description += f"""
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 8px;">{comp.type or 'N/A'}</td>
                    <td style="padding: 8px;"><strong>{comp.make_model or 'N/A'}</strong></td>
                    <td style="padding: 8px; text-align: center;">{comp.qty or 0}</td>
                    <td style="padding: 8px;"><em>{comp.notes or '-'}</em></td>
                </tr>
"""
                
                html_description += """
            </tbody>
        </table>
    </div>
"""
            
            # Uploads Section
            if upload_ids:
                html_description += f"""
    <div style="background-color: #fafafa; padding: 15px; border-radius: 5px; margin-bottom: 20px; border: 2px dashed #9e9e9e;">
        <h3 style="color: #424242; margin-top: 0;">📎 Uploaded Files ({len(upload_ids)})</h3>
        <ul style="list-style-type: none; padding-left: 0;">
"""
                
                for upload_uuid in upload_ids:
                    upload = request.env['project.form.upload'].sudo().search([('uuid', '=', upload_uuid)], limit=1)
                    if upload:
                        # Check if image
                        is_image = False
                        if upload.mime_type and upload.mime_type.startswith('image/'):
                            is_image = True
                        elif upload.name and upload.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                            is_image = True
                        
                        image_url = upload.url
                        if is_image and 'drive.google.com' in upload.url:
                            # Extract ID and convert to direct link
                            # Patterns: /file/d/ID/view, id=ID
                            match = re.search(r'/d/([a-zA-Z0-9_-]+)', upload.url)
                            if match:
                                file_id = match.group(1)
                                image_url = f'https://drive.google.com/uc?export=view&id={file_id}'
                            else:
                                match = re.search(r'id=([a-zA-Z0-9_-]+)', upload.url)
                                if match:
                                    file_id = match.group(1)
                                    image_url = f'https://drive.google.com/uc?export=view&id={file_id}'

                        html_description += f"""
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">
                <a href="{upload.url}" target="_blank" style="color: #1976d2; text-decoration: none; font-weight: bold;">
                    📄 {upload.name}
                </a>
                <span style="background-color: #e0e0e0; padding: 2px 8px; border-radius: 3px; margin-left: 10px; font-size: 12px;">
                    {upload.category or 'General'}
                </span>
"""
                        if is_image:
                             html_description += f"""
                <div style="margin-top: 10px;">
                    <img src="{image_url}" alt="{upload.name}" style="max-width: 100%; max-height: 400px; border-radius: 5px; border: 1px solid #ddd;">
                </div>
"""
                        html_description += """
            </li>
"""
                
                html_description += """
        </ul>
    </div>
"""
            
            html_description += """
</div>
"""
            
            _logger.info("Generated HTML description with %d characters", len(html_description))
            
            # ===== 4. FIND OR CREATE CUSTOMER/PARTNER =====
            partner = request.env['res.partner'].sudo().search([('email', '=', user_profile.email)], limit=1)
            if not partner:
                partner = request.env['res.partner'].sudo().create({
                    'name': user_profile.company_name or user_profile.contact_name,
                    'email': user_profile.email,
                    'phone': user_profile.phone,
                    'is_company': True if user_profile.company_name else False,
                })
                _logger.info("Created partner for %s", user_profile.email)
            
            # ===== 5. FIND APPROPRIATE STAGE =====
            stage = request.env['project.task.type'].sudo().search([
                ('project_ids', 'in', [odoo_project.id]),
                ('name', '=', 'New Job Creation')
            ], limit=1)
            
            if not stage:
                # Get first stage of the project
                stage = request.env['project.task.type'].sudo().search([
                    ('project_ids', 'in', [odoo_project.id])
                ], limit=1)
            
            # ===== 6. CREATE ODOO TASK WITH ALL ENHANCEMENTS =====
            task_values = {
                'name': f"{project.name} - {project.type.upper()}",
                'project_id': odoo_project.id,
                'description': html_description,
                'priority': priority,
                'partner_id': partner.id if partner else False,
                'email_from': user_profile.email,
            }

            # Add engineering firm
            firm_id_val = engineering_firm_data.get('id') or engineering_firm_data.get('uuid') or data.get('engineering_firm_id')
            if firm_id_val:
                firm = request.env['project.form.engineering.firm'].sudo().search([
                    '|', ('uuid', '=', firm_id_val), ('name', '=', firm_id_val)
                ], limit=1)
                if firm:
                    task_values['engineering_firm_id'] = firm.id
            
            # Add tags
            if tag_ids:
                task_values['tag_ids'] = [(6, 0, tag_ids)]
            
            # Add stage
            if stage:
                task_values['stage_id'] = stage.id
            
            odoo_task = request.env['project.task'].sudo().create(task_values)
            
            odoo_task_id = odoo_task.id
            
            # Update project with task ID
            project.write({'odoo_task_id': odoo_task_id})
            
            _logger.info("Created enhanced Odoo task %s for project %s with %d tags, priority %s", 
                        odoo_task_id, project.uuid, len(tag_ids), priority)
        except Exception as e:
            _logger.exception("Failed to create Odoo task: %s", str(e))
            # Don't fail the whole request if task creation fails

        response_data = json.dumps({
            'status': 'success',
            'project_id': project.uuid,
            'user_profile_id': user_profile.uuid,
            'system_summary_id': system_summary_id,
            'battery_info_id': battery_info_id if 'battery_info_id' in locals() else None,
            'site_details_id': site_details_id,
            'electrical_details_id': electrical_details_id,
            'advanced_electrical_details_id': advanced_electrical_details_id,
            'optional_extra_details_id': optional_extra_details_id,
            'system_component_ids': system_component_ids,
            'upload_ids': upload_ids,
            'odoo_task_id': odoo_task_id,
        })
        
        return request.make_response(
            response_data,
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            }
        )



###http://localhost:8069/api/project-updates/<string:project_uuid>
    @http.route('/api/project-updates/<string:project_uuid>', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def get_project_updates(self, project_uuid, **kwargs):
        cors_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        }

        if request.httprequest.method == 'OPTIONS':
            return request.make_response(
                json.dumps({'status': 'ok'}),
                headers=cors_headers
            )

        try:
            # Find the project
            project = request.env['project.form.project'].sudo().search([('uuid', '=', project_uuid)], limit=1)
            if not project:
                headers = {'Content-Type': 'application/json'}
                headers.update(cors_headers)
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Project not found'}),
                    headers=headers,
                    status=404
                )

            # Find the Odoo task
            task_id = project.odoo_task_id
            if not task_id:
                headers = {'Content-Type': 'application/json'}
                headers.update(cors_headers)
                return request.make_response(
                    json.dumps({
                        'status': 'success',
                        'data': {
                            'project_status': project.status,
                            'stage': 'N/A',
                            'subtasks': [],
                            'subtasks_summary': '0 / 0 (0%)',
                            'chat_logs': [],
                            'completion_percentage': 0
                        }
                    }),
                    headers=headers
                )

            task = request.env['project.task'].sudo().browse(task_id)

            # 1. Subtasks
            subtasks_data = []
            completed_subtasks_count = 0
            total_subtasks_count = 0
            
            if hasattr(task, 'child_ids'):
                for child in task.child_ids:
                    total_subtasks_count += 1
                    is_closed = child.stage_id.fold if child.stage_id else False
                    
                    # Enhanced state check for Odoo 16+
                    if hasattr(child, 'state') and child.state in ['1_done', '1_canceled', 'done', 'cancel']:
                         is_closed = True
                    
                    # Fallback: check stage name
                    if not is_closed and child.stage_id and child.stage_id.name in ['Done', 'Cancelled', 'Canceled']:
                        is_closed = True
                    
                    if is_closed:
                        completed_subtasks_count += 1

                    # Get description safely
                    description = child.description if hasattr(child, 'description') else ''
                    
                    subtasks_data.append({
                        'id': child.id,
                        'name': child.name,
                        'stage': child.stage_id.name if child.stage_id else 'New',
                        'is_closed': is_closed,
                        'deadline': str(child.date_deadline) if child.date_deadline else None,
                        'priority': child.priority if hasattr(child, 'priority') else '0',
                        'description': description,
                    })

            # 2. Chat Logs & Tracking
            chat_logs = []
            
            # Fetch messages with tracking values
            # Note: tracking_value_ids is a One2many on mail.message
            messages = request.env['mail.message'].sudo().search([
                ('model', '=', 'project.task'),
                ('res_id', '=', task.id),
                ('message_type', 'in', ['comment', 'notification']), 
            ], order='date desc', limit=50)

            for msg in messages:
                tracking_changes = []
                if hasattr(msg, 'tracking_value_ids') and msg.tracking_value_ids:
                    for val in msg.tracking_value_ids:
                        # DEBUG: Log available fields
                        # _logger.info("Tracking Value Fields: %s", val._fields.keys())
                        
                        # Check for stage change
                        # Try field_id.name first as it is most robust for newer versions
                        is_stage_change = False
                        if 'field_id' in val._fields and val.field_id.name == 'stage_id':
                            is_stage_change = True
                        elif 'field' in val._fields and val.field == 'stage_id':
                            is_stage_change = True
                            
                        if is_stage_change:
                            old_v = val.old_value_char or str(val.old_value_integer) if val.old_value_char or val.old_value_integer else 'None'
                            new_v = val.new_value_char or str(val.new_value_integer) if val.new_value_char or val.new_value_integer else 'None'
                            tracking_changes.append({
                                'field': 'stage_id',
                                'label': 'Stage changed', 
                                'old_value': old_v,
                                'new_value': new_v,
                                'description': f"{old_v} -> {new_v}"
                            })

                log_entry = {
                    'id': msg.id,
                    'date': str(msg.date),
                    'author': msg.author_id.name if msg.author_id else 'System',
                    'body': msg.body, # HTML content
                    'type': msg.message_type,
                    'subtype': msg.subtype_id.name if msg.subtype_id else 'Note',
                    'tracking': tracking_changes
                }
                chat_logs.append(log_entry)

            # 3. Completion Percentage
            completion_percentage = 0
            if total_subtasks_count > 0:
                completion_percentage = round((completed_subtasks_count / total_subtasks_count) * 100)
            elif hasattr(task, 'effective_hours') and hasattr(task, 'planned_hours') and task.planned_hours > 0:
                completion_percentage = round((task.effective_hours / task.planned_hours) * 100)
                if completion_percentage > 100: completion_percentage = 100

            # 4. Assignees
            assignees_data = []
            if hasattr(task, 'user_ids'):
                for user in task.user_ids:
                    assignees_data.append({
                        'id': user.id,
                        'name': user.name,
                        'email': user.email or '',
                    })

            response_data = {
                'status': 'success',
                'data': {
                    'project_id': project.uuid,
                    'project_name': project.name,
                    'status': project.status,
                    'odoo_stage': task.stage_id.name if task.stage_id else 'Unknown',
                    'assignees': assignees_data,
                    'subtasks': subtasks_data,
                    'subtasks_summary': f"{completed_subtasks_count} / {total_subtasks_count} ({completion_percentage}%)",
                    'chat_logs': chat_logs,
                    'completion_percentage': completion_percentage
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            headers.update(cors_headers)
            return request.make_response(
                json.dumps(response_data),
                headers=headers
            )

        except Exception as e:
            _logger.exception("Failed to get project updates: %s", str(e))
            headers = {'Content-Type': 'application/json'}
            headers.update(cors_headers)
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=headers,
                status=500
            )

    @http.route('/api/project/<string:project_uuid>/message', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def post_project_message(self, project_uuid, **kwargs):
        cors_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        }

        if request.httprequest.method == 'OPTIONS':
            return request.make_response(
                json.dumps({'status': 'ok'}),
                headers=cors_headers
            )

        try:
            # Parse body
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except:
                data = request.params

            body = data.get('body')
            if not body:
                headers = {'Content-Type': 'application/json'}
                headers.update(cors_headers)
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Message body is required'}),
                    headers=headers,
                    status=400
                )

            # Find Project & Task
            project = request.env['project.form.project'].sudo().search([('uuid', '=', project_uuid)], limit=1)
            if not project or not project.odoo_task_id:
                headers = {'Content-Type': 'application/json'}
                headers.update(cors_headers)
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Project or Task not found'}),
                    headers=headers,
                    status=404
                )

            task = request.env['project.task'].sudo().browse(project.odoo_task_id)
            
            # Prepare message
            author_name = data.get('author_name', 'Client')
            full_body = f"<p><strong>{author_name} (via Portal):</strong></p><p>{body}</p>"

            # Post message
            task.message_post(
                body=full_body,
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
                # You could try to link to a partner here if you have one, 
                # otherwise it will post as the Odoo Bot/System user but with our custom body.
            )

            headers = {'Content-Type': 'application/json'}
            headers.update(cors_headers)
            return request.make_response(
                json.dumps({
                    'status': 'success',
                    'message': 'Message sent successfully'
                }),
                headers=headers
            )

        except Exception as e:
            _logger.exception("Failed to post message")
            headers = {'Content-Type': 'application/json'}
            headers.update(cors_headers)
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=headers,
                status=500
            )


    @http.route('/api/delete-all', type='http', auth='public', methods=['DELETE', 'OPTIONS'], csrf=False, cors='*')
    def delete_all_projects(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(
                json.dumps({'status': 'ok'}),
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                }
            )
        try:
            projects = request.env['project.form.project'].sudo().search([])
            projects.unlink()
            return request.make_response(
                json.dumps({'status': 'success'}),
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                }
            )
        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                status=500
            )


    
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(
                json.dumps({'status': 'ok'}),
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                }
            )
        try:
            projects = request.env['project.form.project'].sudo().search([])
            return request.make_response(
                json.dumps({'status': 'success', 'projects': projects}),
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                }
            )
        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                status=500
            )

    @http.route('/api/projects/<string:project_id>', type='http', auth='public', methods=['DELETE', 'OPTIONS'], csrf=False, cors='*')
    def delete_project(self, project_id, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(
                json.dumps({'status': 'ok'}),
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                }
            )

        try:
            # Find project by UUID
            project = request.env['project.form.project'].sudo().search([('uuid', '=', project_id)], limit=1)
            
            if not project:
                return request.make_response(
                    json.dumps({
                        'status': 'error',
                        'message': f'Project with ID {project_id} not found'
                    }),
                    headers={
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    status=404
                )

            # Delete associated Odoo task if it exists
            if project.odoo_task_id:
                try:
                    odoo_task = request.env['project.task'].sudo().search([('id', '=', project.odoo_task_id)], limit=1)
                    if odoo_task:
                        odoo_task.unlink()
                        _logger.info("Deleted Odoo task %s for project %s", project.odoo_task_id, project.uuid)
                except Exception as e:
                    _logger.warning("Failed to delete Odoo task %s: %s", project.odoo_task_id, str(e))
                    # Continue with project deletion even if task deletion fails

            # Delete related records (cascade delete)
            # System Summary and Battery Info
            system_summaries = request.env['project.form.system.summary'].sudo().search([('project_id', '=', project.uuid)])
            for summary in system_summaries:
                # Delete battery info first
                battery_infos = request.env['project.form.battery.info'].sudo().search([('system_summary_id', '=', summary.uuid)])
                battery_infos.unlink()
                summary.unlink()

            # Site Details
            site_details = request.env['project.form.site.detail'].sudo().search([('project_id', '=', project.uuid)])
            site_details.unlink()

            # Electrical Details
            electrical_details = request.env['project.form.electrical.detail'].sudo().search([('project_id', '=', project.uuid)])
            electrical_details.unlink()

            # Advanced Electrical Details
            adv_electrical_details = request.env['project.form.advanced.electrical.detail'].sudo().search([('project_id', '=', project.uuid)])
            adv_electrical_details.unlink()

            # Optional Extra Details
            optional_extra_details = request.env['project.form.optional.extra.detail'].sudo().search([('project_id', '=', project.uuid)])
            optional_extra_details.unlink()

            # System Components
            system_components = request.env['project.form.system.component'].sudo().search([('project_id', '=', project.uuid)])
            system_components.unlink()

            # Uploads
            uploads = request.env['project.form.upload'].sudo().search([('project_id', '=', project.uuid)])
            uploads.unlink()

            # Finally, delete the project itself
            project.unlink()

            return request.make_response(
                json.dumps({
                    'status': 'success',
                    'message': f'Project {project_id} and all related records deleted successfully'
                }),
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                }
            )
        except Exception as e:
            _logger.exception("Failed to delete project")
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
    @http.route('/api/projects/update', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def update_project(self, **kwargs):
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
            # Handle both JSON-RPC and plain JSON/form-data
            if request.httprequest.content_type == 'application/json':
                try:
                    data = json.loads(request.httprequest.data.decode('utf-8'))
                except:
                    data = request.params
            else:
                data = request.params
            
            _logger.info("Updating project. Method: %s, Data keys: %s", request.httprequest.method, list(data.keys()) if data else 'None')
            
            project_id = data.get('id')
            if not project_id:
                _logger.warning("Missing project id in update request")
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Missing project id'}),
                    headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    status=400
                )

            project = request.env['project.form.project'].sudo().search([('uuid', '=', project_id)], limit=1)
            if not project:
                _logger.warning("Project not found: %s", project_id)
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Project not found'}),
                    headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    status=404
                )
            
            _logger.info("Found project: %s (ID: %s)", project.name, project.id)

            # Fields to update on the project itself
            project_vals = {}
            if 'name' in data: project_vals['name'] = data['name']
            if 'address' in data: project_vals['address'] = data['address']
            if 'type' in data: project_vals['type'] = data['type']
            if 'general_notes' in data: project_vals['general_notes'] = data['general_notes']
            
            # Handle submission type if name or id is provided
            if 'submission_type_name' in data:
                st = request.env['project.form.submission.type'].sudo().search([('name', '=', data['submission_type_name'])], limit=1)
                if st:
                    project_vals['submission_type_id'] = st.uuid
            elif 'submission_type_id' in data:
                project_vals['submission_type_id'] = data['submission_type_id']

            # Handle services (Many2many)
            if 'services' in data:
                service_ids = data['services']
                service_uuids = []
                for sid in service_ids:
                    if isinstance(sid, str):
                        if '-' in sid and len(sid) == 36:
                            service_uuids.append(sid)
                        else:
                            svc = request.env['project.form.service'].sudo().search([('name', '=', sid)], limit=1)
                            if svc: service_uuids.append(svc.uuid)
                
                if service_uuids:
                    services = request.env['project.form.service'].sudo().search([('uuid', 'in', service_uuids)])
                    project_vals['service_ids'] = [(6, 0, services.ids)]

            if project_vals:
                project.write(project_vals)

            # Update engineering firm on task
            if 'engineering_firm' in data or 'engineering_firm_id' in data:
                firm_data = data.get('engineering_firm', {})
                firm_id_val = firm_data.get('id') or firm_data.get('uuid') or data.get('engineering_firm_id')
                if firm_id_val:
                    firm = request.env['project.form.engineering.firm'].sudo().search([
                        '|', ('uuid', '=', firm_id_val), ('name', '=', firm_id_val)
                    ], limit=1)
                    if firm and project.odoo_task_id:
                        task = request.env['project.task'].sudo().browse(project.odoo_task_id)
                        if task.exists():
                            task.write({'engineering_firm_id': firm.id})

            # Update related models
            # 1. System Summary
            if 'system_summary' in data:
                ss_data = data['system_summary']
                _logger.info("Received system_summary data: %s", ss_data)
                ss = request.env['project.form.system.summary'].sudo().search([('project_id', '=', project.uuid)], limit=1)
                ss_vals = {k: ss_data[k] for k in ['system_size', 'system_type', 'pv_modules', 'inverters'] if k in ss_data}
                if ss:
                    _logger.info("Updating existing system_summary: %s", ss.uuid)
                    ss.write(ss_vals)
                else:
                    _logger.info("Creating new system_summary for project: %s", project.uuid)
                    ss_vals['project_id'] = project.uuid
                    ss = request.env['project.form.system.summary'].sudo().create(ss_vals)

                # Handle Battery Info (inside System Summary)
                if 'battery_info' in ss_data:
                    bi_data = ss_data['battery_info']
                    _logger.info("Received battery_info data: %s", bi_data)
                    bi = request.env['project.form.battery.info'].sudo().search([('system_summary_id', '=', ss.uuid)], limit=1)
                    bi_fields = ['qty', 'model', 'image']
                    bi_vals = {}
                    for f in bi_fields:
                        if f in bi_data:
                            val = bi_data[f]
                            if f == 'image' and isinstance(val, list):
                                val = json.dumps(val)
                            bi_vals[f] = val
                    
                    if bi:
                        _logger.info("Updating existing battery_info: %s", bi.uuid)
                        bi.write(bi_vals)
                    else:
                        _logger.info("Creating new battery_info for system_summary: %s", ss.uuid)
                        bi_vals['system_summary_id'] = ss.uuid
                        request.env['project.form.battery.info'].sudo().create(bi_vals)

            # 2. Site Details
            if 'site_details' in data:
                sd_data = data['site_details']
                _logger.info("Received site_details data: %s", sd_data)
                sd = request.env['project.form.site.detail'].sudo().search([('project_id', '=', project.uuid)], limit=1)
                sd_fields = ['roof_material', 'roof_pitch', 'number_of_arrays', 'ground_mount_type', 'foundation_type', 'main_panel_size', 'utility_provider', 'jurisdiction']
                sd_vals = {k: sd_data[k] for k in sd_fields if k in sd_data}
                if sd:
                    _logger.info("Updating existing site_detail: %s", sd.uuid)
                    sd.write(sd_vals)
                else:
                    _logger.info("Creating new site_detail for project: %s", project.uuid)
                    sd_vals['project_id'] = project.uuid
                    request.env['project.form.site.detail'].sudo().create(sd_vals)

            # 3. Electrical Details
            if 'electrical_details' in data:
                ed_data = data['electrical_details']
                _logger.info("Received electrical_details data: %s", ed_data)
                ed = request.env['project.form.electrical.detail'].sudo().search([('project_id', '=', project.uuid)], limit=1)
                ed_fields = ['main_panel_size', 'bus_rating', 'main_breaker', 'pv_breaker_location', 'one_line_diagram']
                ed_vals = {}
                for f in ed_fields:
                    if f in ed_data:
                        val = ed_data[f]
                        if f == 'one_line_diagram' and isinstance(val, list):
                            val = json.dumps(val)
                        ed_vals[f] = val
                if ed:
                    _logger.info("Updating existing electrical_detail: %s", ed.uuid)
                    ed.write(ed_vals)
                else:
                    _logger.info("Creating new electrical_detail for project: %s", project.uuid)
                    ed_vals['project_id'] = project.uuid
                    request.env['project.form.electrical.detail'].sudo().create(ed_vals)

            # 4. Advanced Electrical Details
            if 'advanced_electrical_details' in data:
                aed_data = data['advanced_electrical_details']
                aed = request.env['project.form.advanced.electrical.detail'].sudo().search([('project_id', '=', project.uuid)], limit=1)
                aed_fields = ['meter_location', 'service_entrance_type', 'subpanel_details']
                aed_vals = {k: aed_data[k] for k in aed_fields if k in aed_data}
                if aed:
                    aed.write(aed_vals)
                else:
                    aed_vals['project_id'] = project.uuid
                    request.env['project.form.advanced.electrical.detail'].sudo().create(aed_vals)

            # 5. Optional Extra Details
            if 'optional_extra_details' in data:
                oed_data = data['optional_extra_details']
                oed = request.env['project.form.optional.extra.detail'].sudo().search([('project_id', '=', project.uuid)], limit=1)
                oed_fields = [
                    'miracle_watt_required', 'miracle_watt_notes', 'der_rlc_required', 'der_rlc_notes',
                    'setback_constraints', 'setback_notes', 'site_access_restrictions', 'site_access_notes',
                    'inspection_notes', 'inspection_notes_text', 'battery_sld_requested', 'battery_sld_notes'
                ]
                oed_vals = {k: oed_data[k] for k in oed_fields if k in oed_data}
                if oed:
                    oed.write(oed_vals)
                else:
                    oed_vals['project_id'] = project.uuid
                    request.env['project.form.optional.extra.detail'].sudo().create(oed_vals)

            # 6. System Components
            if 'system_components' in data:
                sc_data_list = data['system_components']
                # Delete existing ones and recreate
                request.env['project.form.system.component'].sudo().search([('project_id', '=', project.uuid)]).unlink()
                for comp_data in sc_data_list:
                    attachment_urls = comp_data.get('attachment', [])
                    if isinstance(attachment_urls, list):
                        attachment_urls = json.dumps(attachment_urls)
                    
                    request.env['project.form.system.component'].sudo().create({
                        'project_id': project.uuid,
                        'type': comp_data.get('type'),
                        'make_model': comp_data.get('make_model'),
                        'qty': comp_data.get('qty'),
                        'attachment': attachment_urls,
                        'notes': comp_data.get('notes'),
                    })

            return request.make_response(
                json.dumps({
                    'status': 'success',
                    'message': 'Project updated successfully',
                    'project_id': project.uuid
                }),
                headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
            )
        except Exception as e:
            _logger.exception("Failed to update project")
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                status=500
            )

    @http.route('/api/projects', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def get_projects(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(
                json.dumps({'status': 'ok'}),
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                }
            )

        try:
            projects = request.env['project.form.project'].sudo().search([])
            
            # Optimization: Prefetch all linked task stages to avoid N+1 queries
            task_ids = [p.odoo_task_id for p in projects if p.odoo_task_id]
            task_stage_map = {}
            if task_ids:
                tasks = request.env['project.task'].sudo().search([('id', 'in', task_ids)])
                for t in tasks:
                    task_stage_map[t.id] = t.stage_id.name if t.stage_id else None

            data = []
            for project in projects:
                # Fetch User Profile
                user_profile = request.env['project.form.user.profile'].sudo().search([('uuid', '=', project.user_profile_id)], limit=1)
                user_profile_data = {}
                if user_profile:
                    user_profile_data = {
                        'id': user_profile.uuid,
                        'company_name': user_profile.company_name,
                        'contact_name': user_profile.contact_name,
                        'email': user_profile.email,
                        'phone': user_profile.phone,
                    }

                # Fetch Submission Type
                submission_type = request.env['project.form.submission.type'].sudo().search([('uuid', '=', project.submission_type_id)], limit=1)
                submission_type_data = {}
                if submission_type:
                    submission_type_data = {
                        'id': submission_type.uuid,
                        'name': submission_type.name,
                    }

                # Fetch Services
                services_data = []
                for service in project.service_ids:
                    services_data.append({
                        'id': service.uuid,
                        'name': service.name,
                    })

                # Fetch System Summary by searching with project UUID
                system_summary_data = {}
                system_summary = request.env['project.form.system.summary'].sudo().search([('project_id', '=', project.uuid)], limit=1)
                if system_summary:
                    # Fetch Battery Info
                    battery_info_data = {}
                    battery_info = request.env['project.form.battery.info'].sudo().search([('system_summary_id', '=', system_summary.uuid)], limit=1)
                    if battery_info:
                        battery_info_data = {
                            'id': battery_info.uuid,
                            'qty': battery_info.qty,
                            'model': battery_info.model,
                            'image': json.loads(battery_info.image) if battery_info.image else [],
                        }

                    system_summary_data = {
                        'id': system_summary.uuid,
                        'system_size': system_summary.system_size,
                        'system_type': system_summary.system_type,
                        'pv_modules': system_summary.pv_modules,
                        'inverters': system_summary.inverters,
                        'battery_info': battery_info_data
                    }

                # Fetch Site Details by searching with project UUID
                site_details_data = {}
                site_details = request.env['project.form.site.detail'].sudo().search([('project_id', '=', project.uuid)], limit=1)
                if site_details:
                    site_details_data = {
                        'id': site_details.uuid,
                        'roof_material': site_details.roof_material,
                        'roof_pitch': site_details.roof_pitch,
                        'number_of_arrays': site_details.number_of_arrays,
                        'ground_mount_type': site_details.ground_mount_type,
                        'foundation_type': site_details.foundation_type,
                        'main_panel_size': site_details.main_panel_size,
                        'utility_provider': site_details.utility_provider,
                        'jurisdiction': site_details.jurisdiction,
                    }

                # Fetch Electrical Details by searching with project UUID
                electrical_details_data = {}
                electrical_details = request.env['project.form.electrical.detail'].sudo().search([('project_id', '=', project.uuid)], limit=1)
                if electrical_details:
                    electrical_details_data = {
                        'id': electrical_details.uuid,
                        'main_panel_size': electrical_details.main_panel_size,
                        'bus_rating': electrical_details.bus_rating,
                        'main_breaker': electrical_details.main_breaker,
                        'pv_breaker_location': electrical_details.pv_breaker_location,
                        'one_line_diagram': json.loads(electrical_details.one_line_diagram) if electrical_details.one_line_diagram else [],
                    }

                # Fetch Advanced Electrical Details by searching with project UUID
                adv_elec_data = {}
                adv_elec = request.env['project.form.advanced.electrical.detail'].sudo().search([('project_id', '=', project.uuid)], limit=1)
                if adv_elec:
                    adv_elec_data = {
                        'id': adv_elec.uuid,
                        'meter_location': adv_elec.meter_location,
                        'service_entrance_type': adv_elec.service_entrance_type,
                        'subpanel_details': adv_elec.subpanel_details,
                    }

                # Fetch Optional Extra Details by searching with project UUID
                opt_extra_data = {}
                opt_extra = request.env['project.form.optional.extra.detail'].sudo().search([('project_id', '=', project.uuid)], limit=1)
                if opt_extra:
                    opt_extra_data = {
                        'id': opt_extra.uuid,
                        'miracle_watt_required': opt_extra.miracle_watt_required,
                        'miracle_watt_notes': opt_extra.miracle_watt_notes,
                        'der_rlc_required': opt_extra.der_rlc_required,
                        'der_rlc_notes': opt_extra.der_rlc_notes,
                        'setback_constraints': opt_extra.setback_constraints,
                        'setback_notes': opt_extra.setback_notes,
                        'site_access_restrictions': opt_extra.site_access_restrictions,
                        'site_access_notes': opt_extra.site_access_notes,
                        'inspection_notes': opt_extra.inspection_notes,
                        'inspection_notes_text': opt_extra.inspection_notes_text,
                        'battery_sld_requested': opt_extra.battery_sld_requested,
                        'battery_sld_notes': opt_extra.battery_sld_notes,
                    }

                # Fetch System Components by searching with project UUID
                components_data = []
                components = request.env['project.form.system.component'].sudo().search([('project_id', '=', project.uuid)])
                for comp in components:
                    components_data.append({
                        'id': comp.uuid,
                        'type': comp.type,
                        'make_model': comp.make_model,
                        'qty': comp.qty,
                        'attachment': json.loads(comp.attachment) if comp.attachment else [],
                        'notes': comp.notes,
                    })

                # Fetch Uploads by searching with project UUID
                uploads_data = []
                uploads = request.env['project.form.upload'].sudo().search([('project_id', '=', project.uuid)])
                for upload in uploads:
                    uploads_data.append({
                        'id': upload.uuid,
                        'url': upload.url,
                        'name': upload.name,
                        'category': upload.category,
                        'mime_type': upload.mime_type,
                        'size': upload.size,
                    })

                # specific status check with fallback
                project_status = project.status
                if not project_status and project.odoo_task_id in task_stage_map:
                    project_status = task_stage_map[project.odoo_task_id]

                data.append({
                    'id': project.uuid,
                    'name': project.name,
                    'status': project_status,
                    'address': project.address,
                    'type': project.type,
                    'general_notes': project.general_notes,
                    'created_at': str(project.created_at),
                    'updated_at': str(project.updated_at),
                    'user_profile': user_profile_data,
                    'submission_type': submission_type_data,
                    'services': services_data,
                    'system_summary': system_summary_data,
                    'site_details': site_details_data,
                    'electrical_details': electrical_details_data,
                    'advanced_electrical_details': adv_elec_data,
                    'optional_extra_details': opt_extra_data,
                    'system_components': components_data,
                    'uploads': uploads_data,
                })
            
            return request.make_response(
                json.dumps({'status': 'success', 'data': data}, default=str),
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                }
            )
        except Exception as e:
            _logger.exception("Failed to fetch projects")
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                status=500
            )


    @http.route('/api/projects/<string:project_uuid>', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def get_project_by_id(self, project_uuid, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(
                json.dumps({'status': 'ok'}),
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                }
            )

        try:
            project = request.env['project.form.project'].sudo().search([('uuid', '=', project_uuid)], limit=1)
            if not project:
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Project not found'}),
                    headers={
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    status=404
                )
            
            # Determine status with fallback to linked task
            project_status = project.status
            if not project_status and project.odoo_task_id:
                 task = request.env['project.task'].sudo().browse(project.odoo_task_id)
                 if task.exists() and task.stage_id:
                     project_status = task.stage_id.name

            # Fetch User Profile
            user_profile = request.env['project.form.user.profile'].sudo().search([('uuid', '=', project.user_profile_id)], limit=1)
            user_profile_data = {}
            if user_profile:
                user_profile_data = {
                    'id': user_profile.uuid,
                    'company_name': user_profile.company_name,
                    'contact_name': user_profile.contact_name,
                    'email': user_profile.email,
                    'phone': user_profile.phone,
                }

            # Fetch Submission Type
            submission_type = request.env['project.form.submission.type'].sudo().search([('uuid', '=', project.submission_type_id)], limit=1)
            submission_type_data = {}
            if submission_type:
                submission_type_data = {
                    'id': submission_type.uuid,
                    'name': submission_type.name,
                }

            # Fetch Services
            services_data = []
            for service in project.service_ids:
                services_data.append({
                    'id': service.uuid,
                    'name': service.name,
                })

            # Fetch System Summary by searching with project UUID
            system_summary_data = {}
            system_summary = request.env['project.form.system.summary'].sudo().search([('project_id', '=', project.uuid)], limit=1)
            if system_summary:
                # Fetch Battery Info
                battery_info_data = {}
                battery_info = request.env['project.form.battery.info'].sudo().search([('system_summary_id', '=', system_summary.uuid)], limit=1)
                if battery_info:
                    battery_info_data = {
                        'id': battery_info.uuid,
                        'qty': battery_info.qty,
                        'model': battery_info.model,
                        'image': json.loads(battery_info.image) if battery_info.image else [],
                    }

                system_summary_data = {
                    'id': system_summary.uuid,
                    'system_size': system_summary.system_size,
                    'system_type': system_summary.system_type,
                    'pv_modules': system_summary.pv_modules,
                    'inverters': system_summary.inverters,
                    'battery_info': battery_info_data
                }

            # Fetch Site Details by searching with project UUID
            site_details_data = {}
            site_details = request.env['project.form.site.detail'].sudo().search([('project_id', '=', project.uuid)], limit=1)
            if site_details:
                site_details_data = {
                    'id': site_details.uuid,
                    'roof_material': site_details.roof_material,
                    'roof_pitch': site_details.roof_pitch,
                    'number_of_arrays': site_details.number_of_arrays,
                    'ground_mount_type': site_details.ground_mount_type,
                    'foundation_type': site_details.foundation_type,
                    'main_panel_size': site_details.main_panel_size,
                    'utility_provider': site_details.utility_provider,
                    'jurisdiction': site_details.jurisdiction,
                }

            # Fetch Electrical Details by searching with project UUID
            electrical_details_data = {}
            electrical_details = request.env['project.form.electrical.detail'].sudo().search([('project_id', '=', project.uuid)], limit=1)
            if electrical_details:
                electrical_details_data = {
                    'id': electrical_details.uuid,
                    'main_panel_size': electrical_details.main_panel_size,
                    'bus_rating': electrical_details.bus_rating,
                    'main_breaker': electrical_details.main_breaker,
                    'pv_breaker_location': electrical_details.pv_breaker_location,
                    'one_line_diagram': json.loads(electrical_details.one_line_diagram) if electrical_details.one_line_diagram else [],
                }

            # Fetch Advanced Electrical Details by searching with project UUID
            adv_elec_data = {}
            adv_elec = request.env['project.form.advanced.electrical.detail'].sudo().search([('project_id', '=', project.uuid)], limit=1)
            if adv_elec:
                adv_elec_data = {
                    'id': adv_elec.uuid,
                    'meter_location': adv_elec.meter_location,
                    'service_entrance_type': adv_elec.service_entrance_type,
                    'subpanel_details': adv_elec.subpanel_details,
                }

            # Fetch Optional Extra Details by searching with project UUID
            opt_extra_data = {}
            opt_extra = request.env['project.form.optional.extra.detail'].sudo().search([('project_id', '=', project.uuid)], limit=1)
            if opt_extra:
                opt_extra_data = {
                    'id': opt_extra.uuid,
                    'miracle_watt_required': opt_extra.miracle_watt_required,
                    'miracle_watt_notes': opt_extra.miracle_watt_notes,
                    'der_rlc_required': opt_extra.der_rlc_required,
                    'der_rlc_notes': opt_extra.der_rlc_notes,
                    'setback_constraints': opt_extra.setback_constraints,
                    'setback_notes': opt_extra.setback_notes,
                    'site_access_restrictions': opt_extra.site_access_restrictions,
                    'site_access_notes': opt_extra.site_access_notes,
                    'inspection_notes': opt_extra.inspection_notes,
                    'inspection_notes_text': opt_extra.inspection_notes_text,
                    'battery_sld_requested': opt_extra.battery_sld_requested,
                    'battery_sld_notes': opt_extra.battery_sld_notes,
                }

            # Fetch System Components by searching with project UUID
            components_data = []
            components = request.env['project.form.system.component'].sudo().search([('project_id', '=', project.uuid)])
            for comp in components:
                components_data.append({
                    'id': comp.uuid,
                    'type': comp.type,
                    'make_model': comp.make_model,
                    'qty': comp.qty,
                    'attachment': json.loads(comp.attachment) if comp.attachment else [],
                    'notes': comp.notes,
                })

            # Fetch Uploads by searching with project UUID
            uploads_data = []
            uploads = request.env['project.form.upload'].sudo().search([('project_id', '=', project.uuid)])
            for upload in uploads:
                uploads_data.append({
                    'id': upload.uuid,
                    'url': upload.url,
                    'name': upload.name,
                    'category': upload.category,
                    'mime_type': upload.mime_type,
                    'size': upload.size,
                })

            project_data = {
                'id': project.uuid,
                'name': project.name,
                'status': project_status,
                'address': project.address,
                'type': project.type,
                'general_notes': project.general_notes,
                'created_at': str(project.created_at),
                'updated_at': str(project.updated_at),
                'user_profile': user_profile_data,
                'submission_type': submission_type_data,
                'services': services_data,
                'system_summary': system_summary_data,
                'site_details': site_details_data,
                'electrical_details': electrical_details_data,
                'advanced_electrical_details': adv_elec_data,
                'optional_extra_details': opt_extra_data,
                'system_components': components_data,
                'uploads': uploads_data,
            }

            return request.make_response(
                json.dumps({'status': 'success', 'data': project_data}, default=str),
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                }
            )
        except Exception as e:
            _logger.exception("Failed to fetch project")
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                status=500
            )
