[![Build
status](https://travis-ci.org/parksandwildlife/ledger.svg?branch=master)](https://travis-ci.org/parksandwildlife/ledger/builds) [![Coverage Status](https://coveralls.io/repos/github/parksandwildlife/ledger/badge.svg?branch=master)](https://coveralls.io/github/parksandwildlife/ledger?branch=master)
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
    DATABASE_URL="postgres://USER:PASSWORD@HOST:PORT/NAME"
    SECRET_KEY="ThisIsASecretKey"

# Wildlife Licensing

This section contains information specific to the Wildlife Licensing projects.

## Creating Licence Types

Each wildlife licence type, whether free or paid, needs an equivalent product in the Django Oscar payments system. These
are linked by the `Product Title` attribute of the Wildlife licence types.

** Note: you must create a the product in Oscar before creating the licence type. **

### Creating a Product in Oscar

To access the Oscar dashboard, select `Oscar Dashboard` under the Options menu (must be a *staff* user). From there, 
select `Products` under the `Cataloge` menu. You will then see the existing products and also a blue button with `+ New
Product` which should be pressed to begin creating a new product.

#### Product Details

`Title` is what will be used to link the product to the wildlife licence type. It will also be visible on the invoice 
so should be succinct but meaningful.

`Oracle Code` - TODO

`Is discountable` - If the product will be discountable for seniors, check this checkbox.

#### Stock and pricing

Click `Stock and pricing` on the left-side menu to get to this section. You must fill in all fields. 

`Partner` - select the only option available TODO (find out what this is).

`SKU` - TODO find out what this is.

`Currency` - enter AUD

`Cost price`, `Price (excl tax)`, `Retail price` - these should all be the same, which is the cost of licence. Enter 
0.00 if the licence is free.

Once you've entered these details, click the blue `Save` button on the bottom right.

### Creating a Wildlife licence type

To create a new wildlife licence type, go to admin (*staff* users only) under the options menu item at the top right.
At the bottom of the admin section, under the WL MAIN section, click the add button next to Wildlife licence types. From
there, enter the fields as follows (only bold fields are mandatory).

`Effective to: This field is currently not in use and can be left blank.

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
their own set of fields. These can be further nested into groups of fields if required.

```json
[
  {
    section 1
    [
      field 1,
      field 2,
    ]
  },
  {
     section 2,
     [
      field 3,
      field 4
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

`label` is the piece of text proceeding an input and is usually the question to be answered in the input.

##### Field-specific Attributes

With several fields there are extra attributes required.

