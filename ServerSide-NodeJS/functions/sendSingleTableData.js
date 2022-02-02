const sendSingleTableData = (restaurantID, password, tableIndex) => {
    return new Promise((resolve, reject) => {
        if (restaurantID != undefined && password != undefined && restaurantID != null && password != null && tableIndex != undefined && tableIndex != null) {
            if (restaurantID.length > 0) {
                if (password.length > 0) {
                    if (!isNaN(tableIndex)) {
                        Client.find({restaurantID}).then(cliRes => {
                            console.log(cliRes);
                            if (cliRes.length > 0) {
                                if (cliRes[0].tablesData.length > tableIndex && cliRes[0].tablesData[tableIndex] != undefined && cliRes[0].tablesData[tableIndex] != null) {
                                    if (cliRes[0].password == password) {
                                        // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                        // ~~~~~~~~~~~~~~~~~ Authentication Successfull ~~~~~~~~~~~~~~~~~
                                        console.log("sucesful single table request!");
                                        resolve({validity: true, tablesData: cliRes[0].tablesData[tableIndex]});
            
                                    } else reject({validity: false, msg: "Invalid password;"});
                                } else reject({validity: false, msg: "Invalid table id;"});
                            } else reject({validity: false, msg: "Restaurant ID doesn't exist;"});
                        }).catch(err => console.log(err));
                    } else reject({validity: false, msg: `Table index has to be an integer, not a ${typeof tableIndex}`})
                } else reject({validity: false, msg: "Password not entered;"});
            } else reject({validity: false, msg: "Restaurant ID or password is undefined;"});
        } else reject({validity: false, msg: "Restaurant ID not entered;"});
        // Returning an "error with the server message" as this case here is only hit if the database connection returns an error;
        return {validity: false, msg: "Server has issues, Please notify Alcoft"};
    });
};


module.exports = sendSingleTableData;