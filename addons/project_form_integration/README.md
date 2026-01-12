# Project Form Integration - API Documentation

## Installation

```bash
./odoo-bin -c odoo.conf -i project_form_integration -d your_database
```

## API Endpoint

**URL:** `POST /api/create-project`

**Auth:** Public

**Content-Type:** `application/json`

## Request Payload

```json
{
  "user_profile": {
    "company_name": "Solar Solutions Inc",
    "contact_name": "John Doe",
    "email": "john@solarsolutions.com",
    "phone": "+1234567890"
  },
  "project": {
    "name": "Commercial Solar Installation",
    "address": "123 Main St, City, State",
    "type": "Commercial",
    "submission_type_id": 1,
    "general_notes": "Urgent project"
  },
  "services": [1, 2, 3],
  "system_summary": {
    "system_size": 50.5,
    "system_type": "Grid-Tied",
    "pv_modules": 120,
    "inverters": 3
  },
  "battery_info": {
    "qty": 4,
    "model": "Tesla Powerwall 2",
    "image": ["https://drive.google.com/file/d/xxx", "https://drive.google.com/file/d/yyy"]
  },
  "site_details": {
    "roof_material": "TPO",
    "roof_pitch": "Flat",
    "number_of_arrays": 3,
    "utility_provider": "ComEd",
    "jurisdiction": "Chicago"
  },
  "electrical_details": {
    "main_panel_size": "400A",
    "bus_rating": "400A",
    "main_breaker": "400A",
    "pv_breaker_location": "BOTTOM",
    "one_line_diagram": ["https://drive.google.com/file/d/zzz"]
  },
  "advanced_electrical_details": {
    "meter_location": "Exterior south wall",
    "service_entrance_type": "Underground",
    "subpanel_details": "200A subpanel"
  },
  "optional_extra_details": {
    "miracle_watt_required": false,
    "der_rlc_required": true,
    "der_rlc_notes": "Required by utility",
    "setback_constraints": true,
    "setback_notes": "3ft from edge",
    "site_access_restrictions": false,
    "inspection_notes": true,
    "inspection_notes_text": "Coordinate with building manager",
    "battery_sld_requested": true,
    "battery_sld_notes": "Include AC/DC coupling"
  },
  "system_components": [
    {
      "type": "Solar Module",
      "make_model": "Canadian Solar CS3W-420P",
      "qty": 120,
      "attachment": ["https://drive.google.com/file/d/aaa"],
      "notes": "High efficiency"
    },
    {
      "type": "Inverter",
      "make_model": "SolarEdge SE16.8K",
      "qty": 3,
      "attachment": ["https://drive.google.com/file/d/bbb"],
      "notes": "With RGM"
    }
  ],
  "uploads": [
    {
      "url": "https://drive.google.com/file/d/ccc",
      "name": "Site Plan",
      "category": "Documents",
      "mime_type": "application/pdf",
      "size": 2048576
    }
  ]
}
```

## Response

```json
{
  "status": "success",
  "project_id": 42,
  "user_profile_id": 5,
  "system_summary_id": 12,
  "battery_info_id": 8,
  "site_details_id": 15,
  "electrical_details_id": 18,
  "advanced_electrical_details_id": 20,
  "optional_extra_details_id": 22,
  "system_component_ids": [30, 31],
  "upload_ids": [45]
}
```

## Models

- `project.form.user.profile`
- `project.form.submission.type`
- `project.form.service`
- `project.project` (inherited)
- `project.form.system.summary`
- `project.form.battery.info`
- `project.form.site.detail`
- `project.form.electrical.detail`
- `project.form.advanced.electrical.detail`
- `project.form.optional.extra.detail`
- `project.form.system.component`
- `project.form.upload`

## Features

- Extends `project.project` with custom fields
- Stores Google Drive URLs (no binary uploads)
- Creates/reuses user profiles by email
- Supports nested data creation
- Public API access
- JSON array storage for multiple URLs





### Project module creation
To automatically create a project task in Odoo's built-in Project module after creating your custom project, you need to:

How It Works
Odoo's Project Module uses the project.project model for projects and project.task model for tasks
After successfully creating your custom project record, you'll use Odoo's ORM to create a corresponding task in the standard Project module
You can link the custom project to the Odoo task by storing the task ID
Implementation Approach
python
# After creating your custom project:
project = request.env['project.form.project'].sudo().create({...})

# Create a task in Odoo's project module
odoo_task = request.env['project.task'].sudo().create({
    'name': f"Project: {project.name}",
    'description': f"""
        Address: {project.address}
        Type: {project.type}
        Notes: {project.general_notes}
    """,
    'project_id': 1,  # ID of the Odoo project to assign to (you need to create/find this)
    # Optional fields:
    'partner_id': user_profile.partner_id,  # If you link user profiles to partners
    'priority': '1',  # High priority
    'date_deadline': fields.Date.today() + timedelta(days=30),
})
Questions Before Implementation
Do you have an existing Odoo Project to assign tasks to, or should I create one programmatically?
What information from your custom project should appear in the Odoo task?
Should I store the Odoo task ID in your custom 
projects
 table for future reference?