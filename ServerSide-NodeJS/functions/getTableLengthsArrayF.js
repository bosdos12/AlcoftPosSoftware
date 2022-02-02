const getTableLengthsArrayF = (tableArrays) => {
    // Return array;
    let returnArray = [];
    // Looping through each table element for the length of the tables array so we can get the values of the filled and empty tables;
    for (arr of tableArrays) {
        if (arr.tBill.length > 0) {
            // Adding true to this index of the returnArray as it has items in it;
            returnArray.push(true);
        } else returnArray.push(false) // Otherwise, pushing a false to the array;
    }
    // Returning the return array;
    return returnArray;
};


module.exports = getTableLengthsArrayF;