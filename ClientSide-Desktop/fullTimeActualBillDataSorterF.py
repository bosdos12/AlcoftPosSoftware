def fullTimeActualBillDataSorterF(BillParData):
    # Creating an object which will keep all the data as sortings occur/data will be added/kept in it + it will be used in the app;
    returnObjectBillData = {"tbp": 0, "tBill": []}
    print(BillParData)
    # Sorting the data;
    for billItem in BillParData["tablesData"]["tBill"]:
        returnObjectBillData["tBill"].append({"n": billItem["n"], "c": billItem["c"], "p": billItem["p"]})


    returnObjectBillData["tbp"]          = BillParData["tablesData"]["tbp"]
    returnObjectBillData["SaleTime"]     = BillParData["SaleTime"]
    returnObjectBillData["totalWithTax"] = BillParData["totalWithTax"]
    returnObjectBillData["compName"]     = BillParData["compName"]
    returnObjectBillData["taxValue"]     = BillParData["taxValue"]


    # Returning the bill object back so it can be written to the json file;
    return returnObjectBillData
        





"""
def fullTimeActualBillDataSorterF(BillParData):
    # Creating an object which will keep all the data as sortings occur/data will be added/kept in it + it will be used in the app;
    returnObjectBillData = {"tbp": 0, "tBill": {}}
    print(BillParData)
    # Sorting the data;
    for billItem in BillParData["tablesData"]["tBill"]:
        if billItem["n"] in returnObjectBillData["tBill"]:
            returnObjectBillData["tBill"][billItem["n"]]["c"]+=billItem["c"]
        else:
            returnObjectBillData["tBill"][billItem["n"]] = billItem
        

    returnObjectBillData["tbp"] = BillParData["tablesData"]["tbp"]

    return returnObjectBillData # FUCKING HELL BRUV #BUG #TODO #NOTE #







    for billItem in BillParData["tablesData"]["tBill"]:
        if billItem["n"] in returnObjectBillData["tBill"]:
            returnObjectBillData["tBill"][billItem["n"]]["c"] += billItem['c']
        else:
            returnObjectBillData["tBill"][billItem["n"]] = {"p": billItem["p"], "c": billItem["c"]}
"""