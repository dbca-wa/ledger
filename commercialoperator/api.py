
def post(self, request, *args, **kwargs):

    lines = []
    for row in tbody:
        park_id = row[0]['value']
        arrival = row[1]
        no_adults = int(row[2])
        no_children = int(row[3])
        park= Park.objects.get(id=park_id)
        ledger_description = row[1] + '. ' + park.name + ' (' + row[2] + ' Adults' + ')'
        oracle_code = 'ABC123 GST'
        price_incl_tax = str(park.adult * int(no_adults))
        quantity = 1

        if row[1]:
            llines.append(dict(
                ledger_description = arrival + '. ' + park.name + ' (' + str(no_adults) + ' Adults' + ')',
                oracle_code = 'ABC123 GST',
                price_incl_tax = Decimal(park.adult * int(no_adults)),
                quantity = 1
            ))
            print row[1] + '. ' + park.name[1] + '. ' + park.name + '. Adults: ' + row[2] + ', Price: ' + str(park.adult * int(no_adults))

        if row[2]:

            lines.append(dict(
                ledger_description = arrival + '. ' + park.name + ' (' + str(no_children) + ' Children' + ')',
                oracle_code = 'ABC123 GST',
                price_incl_tax = Decimal(park.child * int(no_children)),
                quantity = 1
            ))
            print row[1] + '. ' + park.name + '. Children: ' + row[3] + ', Price: ' + str(park.adult * int(no_children))

        print


