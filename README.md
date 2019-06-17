[![Build
status](https://travis-ci.org/dbca-wa/ledger.svg?branch=master)](https://travis-ci.org/dbca-wa/ledger/builds) [![Coverage Status](https://coveralls.io/repos/github/dbca-wa/ledger/badge.svg?branch=master)](https://coveralls.io/github/dbca-wa/ledger?branch=master)
# Ledger

This project is the hub of the Department's online commerce activities.
It provides authentication, address and online payments functionality.

# Requirements

- Python (2.7.x)
- PostgreSQL (>=9.3)

Python library requirements should be installed using `pip`:

`pip install -r requirements.txt`

# Environment settings

A `.env` file should be created in the project root and used to set
required environment variables at run time. Example content:

    DEBUG=True
    DATABASE_URL="postgis://USER:PASSWORD@HOST:PORT/NAME"
    SECRET_KEY="ThisIsASecretKey"
    DEFAULT_HOST="https://website.domain/"
    EMAIL_HOST="emailhost"
    EMAIL_FROM="system@email.address"
    PARENT_HOST="website.domain"
    HOST_PORT=""
    ALLOWED_HOSTS=[u'website.domain']
    CMS_URL="https://url-used-to-retrieve-system-id-via-api/"
    LEDGER_USER="UserForSystemIdAPI"
    LEDGER_PASS="Password"
    BPOINT_BILLER_CODE="1234567"
    BPOINT_USERNAME="Username"
    BPOINT_PASSWORD="Password"
    BPOINT_MERCHANT_NUM="1234567889012345"
    BPAY_BILLER_CODE="123456"
    BPAY_FILE_PATH="/file/path/for/incoming/bpay/files"
    OSCAR_SHOP_NAME="Shop 1"
    NOTIFICATION_EMAIL="email@for.bpay.notifications"
    PRODUCTION_EMAIL=False (Send system emails to NON_PROD_EMAIL if False)
    EMAIL_INSTANCE='UAT' (DEV/TEST/UAT/PROD)
    NON_PROD_EMAIL='comma@separated.email,listfor@nonproduction.emails'
    LOG_CONSOLE_LEVEL='INFO'

# Docker image builds

Individual Dockerfiles have been created for each derivative application. To
build a new image for an application (e.g. Parkstay Bookings):

1. Ensure that any required frontend assets have been built (`cd
   parkstay/frontend/parkstay && npm run build`)
2. Copy the relevant Dockerfile to the root of the project (e.g. `cp parkstay/Dockerfile .`)
3. Build the Docker image as normal (e.g. `docker image build -t dbcawa/parkstay .`)

# Parkstay Bookings

To set the API endpoint URL for frontend JS apps, set the following env var:

    PARKSTAY_URL="http://hostname:port"

# Wildlife Licensing

This section contains information specific to the Wildlife Licensing projects.

## Creating Licence Types

Each wildlife licence type, whether free or paid, needs an equivalent product in the Django Oscar payments system. These
are linked by the `Product Title` attribute of the Wildlife licence types.

**Note: you must create the product in Oscar before creating the licence type.**

### Creating a Product in Oscar

To access the Oscar dashboard, select `Oscar Dashboard` under the Options menu (must be a *staff* user). From there,
select `Products` under the `Cataloge` menu. You will then see the existing products and also a blue button with `+ New
Product` which should be clicked to begin creating a new product.

#### Product Details

`Title`: What will be used to link the product to the wildlife licence type. It will also be visible on the invoice
so should be succinct but meaningful.

`Oracle Code`: The account code in Oracle Finance where the revenue should be booked to.

`Is discountable`: If the product will be discountable for seniors, check this checkbox.

#### Stock and pricing

Click `Stock and pricing` on the left-side menu to get to this section. You must fill in all fields.

`Partner`: select the only option available which should be Wildlife Licensing.

`SKU`: Stock Keeping Unit - this field is not used by requires a value, so any random unique is acceptable.

`Currency`: Enter AUD

`Cost price`, `Price (excl tax)`, `Retail price`: These should all be the same, which is the cost of licence. Enter
0.00 if the licence is free.

Once you've entered these details, click the blue `Save` button on the bottom right.

### Creating a Wildlife licence type

To create a new wildlife licence type, go to admin (*staff* users only) under the options menu item at the top right.
At the bottom of the admin section, under the WL MAIN section, click the add button next to Wildlife licence types. From
there, enter the fields as follows (only bold fields are mandatory).

`Effective to`: This field is currently not in use and can be left blank.

`Name`: The full title of the licence type, e.g. *Licence to take fauna for scientfic purposes*

`Short Name`: This is the name which will be shown in the list of licences in the dashboard so that it fits in the column
and is readable. e.g. *fauna licence sci.*

`Version`: The version number of the licence. If the application schema of the licence changes at all,
you need to create a new version of the licence, rather than change the current licence. e.g. *1*

`Code`: The regulation code of the licence. e.g. *Regulation 17*

`Act`: The licence act that will appear on the licence PDF. e.g. 'Wildlife Conservation Act 1950'

`Statement`: A legal statement which will appear on the licence PDF e.g. *The undermentioned person may take fauna for
research or other scientific purposes and where authorised, keep it in captivity, subject to the following and
attached conditions, which may be added to, suspended or otherwise varied as considered fit.*

`Authority`: The legal authority which will appear on the licence PDF e.g. *Director General*.

`Replaced by`: If you're creating a new version of a licence, once complete, you need edit the previous version of the
licence and select the newest version.

`Is renewable`: The default for whether a particular licence of this type will be renewable. This is just the default
value and can be changed by an officer when issuing the licence.

`Key words`: This field is currently not in use and can be left blank.

`Product title`: This is the field which is used to link the licence to the Oscar product discussed in the previous
section. This needs to match the product title exactly.

`Identification required`: Whether the licence requires photo ID.

`Senior applicable`: Whether this licence can be discounted for seniors.

`Application schema`: The `json` schema for the application questionaire. This will be discussed in detail in the next
section.

`Category`: The category the licence falls within, which will be used in the licence type selection screen for users.
e.g. *Fauna Licences*.

`Variant Group`: The group of variants of this licence. This will be discussed in detail in a later section.

`Help text`: Descriptive text for the licence which is shown under the licence type in the licence type selection screen
for users.

`Default conditions`: These are the conditions that appear by default under the `Enter conditions` page for officers when
processing a licence. There can be as many default conditions as required. To enter each, select the condition and enter
an order number, which dictates the order in which they appear on the enter conditions page and on the licence PDF.

When all mandatory fields have been entered, click the blue `Save` button at the bottom-right.

#### Application Schema

The application schema describes the fields that will be shown in the application questionaire, under the "Enter
Details" heading. This is in the JSON format and must, at the highest level, contain a list of sections, each with
their own set of fields (although a section is a type of field itself in this paradigm). These can be further nested
into groups of fields if required. A very simple example is shown below.

```
[
    {
        "type": "section",
        "name": "section_1",
        "label": "Section 1"
        "children": [
            {
                "type": "text",
                "name": "name",
                "label": "Provide you name"
            },
            {
                "type": "file",
                "name": "qualification_attachments",
                "label": "Qualification Attachment(s)"
            },
            {
                "type": "declaration",
                "name": "acknowledgement",
                "label": "I acknowledge that all this information is true"
            }
        ]
    },
    {
        "type": "section",
        "name": "section_2",
        "label": "Section 2"
        "children": [
            {
                "type": "text",
                "name": "additional_info",
                "label": "Provide relevant additional information"
            },
            {
                "type": "declaration",
                "name": "acknowledgement",
                "label": "I acknowledge that all this information is true"
            }
        ]
    }
]
```

##### Mandatory Attributes

All fields, including sections and groups, must at minimum contain three attributes: `type`, `name`, and `label`.

`type` is generally for html input types, except in a few cases, such as `section`, `group`, and `label`. The available
types are:

* `section` - base section for grouping fields
* `group` - nested group of fields within section or other groups
* `text` - standard text input
* `text_area` - large text input
* `number` - number input
* `date` - date input
* `select` - combo box input
* `radiobuttons` - radio button group input
* `checkbox` - single checkbox input
* `label` - just text-based label (usually goes before series of checkboxes)
* `file`- file input
* `declaration` - checkbox with declaration text next to it.
* `species` - special species lookup input

`name` is a field for identifying each field in the system. **Note: every field must have a totally unique name**. This
means no two fields anywhere in one application schema can have have the same name. Also note that the name cannot
contain spaces or special characters such as question marks, full stops, etc.

`label` is the piece of text preceding an input and is usually the question to be answered in the input.

##### Non-mandatory Attributes

There is also a non-mandatory attribute that can go with each field.

* `help_text` - Text that will appear under each field, usually an explanation or example answer to a question.

##### Field-specific Attributes
With several fields there are extra attributes required which are detailed below.

###### Groups / Sections
Sections and groups both require a `children` attribute, which is a list of fields are listed within.

Groups can also have a field called `isRepeatable` for when the whole group needs be be repeated on the questionaire
to allow repeated entries of the same type of certain data, such as a list of people's various details. An example group field is shown below.

```
{
    "type": "group",
    "name": "authorised_persons",
    "label": "Authorised Person",
    "isRepeatable": true,
    "children": [
        {
            "type": "text",
            "name": "ap_surname",
            "label": "Surname"
        },
        {
            "type": "checkbox",
            "name": "ap_given_names",
            "label": "Given name(s)"
        },
        {
            "type": "date",
            "name": "ap_dob",
            "label": "Date of birth"
        }
    ]
}
```

###### Select / Radiobuttons

These fields require an `options` attribute, which is the list of options for either the combo box or set of
radiobuttons. This is a list of objects with each object requiring a `value` and `label` attribute. `value` is the
actual value that will be stored in the database and `label` is the verbose version of the value. An optional field `defaultBlank` can be set to true if the initial chosen option in the combo box should be blank for `select` fields or no radiobuttons selected for `radiobuttons` fields. If `defaultBlank` is not set or false, the first option will be selected as default.

```
{
    "type": "select",
    "name": "ap_association",
    "label": "Association to applicant",
    "defaultBlank": true
    "options": [
        {
            "value": "volunteer",
            "label": "Volunteer"
        },
        {
            "value": "contractor",
            "label": "Contractor"
        },
        {
            "value": "staff",
            "label": "Staff / Employee"
        },
        {
            "value": "student",
            "label": "Student"
        },
        {
            "value": "other",
            "label": "Other - Please provide details"
        }
    ]
}
```

###### Checkboxes

Checkboxes differ slightly from other fields in that while they are often grouped together, they exist as separate
fields. In the case of checkbox fields, the label will appear next to the checkbox, rather than above, such that when
there is a sequence of checkbox fields they appear grouped together. As a result, a label field is usually required
before the sequence of checkbox fields, which will contain the question. This should not be confused with the label
attribute of a field - it is a field in its own right, and should have a label attribute within.

```
{
    "type": "label",
    "name": "ap_handler_type",
    "label": "Handler Type"
},
{
    "type": "checkbox",
    "name": "ap_basic",
    "label": "Basic handling, trap clearing and animal measurements"
},
{
    "type": "checkbox",
    "name": "ap_biopsy",
    "label": "Biopsy/tissue samples"
},
{
    "type": "checkbox",
    "name": "ap_chipping",
    "label": "Microchipping/tagging"
}
```

##### Conditions
There may be cases where a field or set of fields should only be shown if a particular answer is given for an earlier
field. To accomplish this, the `condition` attribute can be added to most field types, with the exception of
`section`, `group`, `label` and `file`. In practice, however, generally conditions would only be applied to
`select`, `radiobutton` and `checkbox` fields. A condition attribute should itself be a object, where each
attribute name is the answer that will yield further fields and the value of each attribute is the actual list of such
fields. Note: not all options require an entry in `conditions`, only the values that require further fields.

```
{
    "type": "radiobuttons",
    "name": "how_project_funded",
    "label": "How is your project funded?",
    "options": [
        {
            "value": "grant",
            "label": "Grant / Sponsored"
        },
        {
            "value": "contract",
            "label": "Contract / Consulting"
        },
        {
            "value": "other",
            "label": "Other - Please provide details"
        }
    ],
    "conditions": {
        "grant": [
            {
                "type": "text_area",
                "name": "grant_details",
                "label": "Provide details of the grant or sponsorship"
            }
        ],
        "contract": [
            {
                "type": "text",
                "name": "contract_client_name",
                "label": "Provide the client name."
            },
            {
                "type": "text_area",
                "name": "contract_client_address",
                "label": "Provide the client address."
            }
        ],
        "other": [
            {
                "type": "text_area",
                "name": "financial_details_other",
                "label": "Provide details of who is funding the project or how the project is being funded"
            }
        ]
    }
}
```

##### Licence Fields

There may be cases where particular questions/answers need to appear on the actual licence(namly the PDF), which are
termed *licence fields*. These licence fields will be available to be adjusted by officers just before the licence is
issued. To declare a field as being a licence field, specify the attribute `isLicenceField: true`. There are a number
of optional fields that also relate to licence fields, which are:

* `licenceFieldLabel` - Text to replace the default label text on the actual licence.
* `licenceFieldHelpText` - Additional help text to show with each licence field. Note that by default, no help text
will be shown on licences (i.e. the normal `helpText` for the field won't show, only the `licenceFieldHelpText`
text.
* `isLicenceFieldReadonly` - If true, officers cannot adjust the content of the licence field answer before issuing
the licence.

```
{
    "type": "text",
    "name": "applicant_surname",
    "label": "Surname",
    "isLicenceField": true,
    "licenceFieldLabel": "The surname of the applicant",
    "licenceFieldHelpText": "This would be the last name of the person who is applying for the licence"
}
```

In the case of groups, the group field itself must be a declared licence field along with any children fields within
the group that should appear on the actual licence. These fields will then be grouped together within the licence.
Note that this only goes one level in, i.e. children of chilren within a group would not appear grouped with the parent
group. In the example below, the species that can be taken within the licence period will be grouped together on the
licence, as the group is repeatable. Only the species name and count will appear though, as only these have been
specified as licence fields.

```
{
    "type": "group",
    "name": "species_taken",
    "label": "Species that are taken",
    "isRepeatable": true,
    "isLicenceField": true,
    "licenceFieldLabel": "Species taken within the study",
    "licenceFieldHelpText": "All species that may be taken are taken for study throughout the licence period"
    "children": [
        {
            "type": "text",
            "name": "species_scientific_name",
            "label": "Species Scientific Name",
            "isLicenceField": true
        },
        {
            "type": "text",
            "name": "species_common_name",
            "label": "Species common name"
        },
        {
            "type": "number",
            "name": "species_count",
            "label": "Species Count",
            "isLicenceField": true
        }
    ]
}
```
