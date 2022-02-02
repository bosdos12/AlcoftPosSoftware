const validateUserF = (restaurantID, password) => {
    return new Promise((resolve, reject) => {
        if (restaurantID != undefined && password != undefined && restaurantID != null && password != null) {
            if (restaurantID.length > 0) {
                if (password.length > 0) {
                    Client.find({restaurantID}).then(cliRes => {
                        console.log(cliRes);
                        if (cliRes.length > 0) {
                            if (cliRes[0].password == password) {
                                // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                // ~~~~~~~~~~~~~~~~~ Authentication Successfull ~~~~~~~~~~~~~~~~~
                                console.log("yeet!");
                                resolve({validity: true, clientData: cliRes[0]});
    
                            } else reject({validity: false, msg: "Invalid password;"});
                        } else reject({validity: false, msg: "Restaurant ID doesn't exist;"});
                    }).catch(err => console.log(err));
                } else reject({validity: false, msg: "Password not entered;"});
            } else reject({validity: false, msg: "Restaurant ID or password is undefined;"});
        } else reject({validity: false, msg: "Restaurant ID not entered;"});
        // Returning an "error with the server message" as this case here is only hit if the database connection returns an error;
        return {validity: false, msg: "Server has issues, Please notify Alcoft"};
    })
}

module.exports = validateUserF;