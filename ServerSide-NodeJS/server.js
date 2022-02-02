const express = require("express");
const mongoose = require("mongoose");
const app = express();

// Schemas;
let Client = require("./schema/Client.js");

// Functions;
const getTableLengthsArrayF = require("./functions/getTableLengthsArrayF.js");


// App Data;
let DBURI = "NO!";
let PORT = 80;

// Setting the views;
app.set("views", "views");
app.set("view engine", "ejs");

// Allowing json data to be parsed.
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// Setting the public directory;
app.use(express.static(__dirname + "/Public"));

// Starting the server
mongoose.connect(DBURI, {useUnifiedTopology: true, useNewUrlParser: true, useFindAndModify: false}).then(() => {
    app.listen(PORT, () => console.log(`[THE SERVER HAS STARTED RUNNING ON PORT ${PORT}]`));
})

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Just website
app.get("/", (req, res) => {
    res.render("index");
});
app.get("/clients", (req, res) => {
    res.render("clients");
});
app.get("/products", (req, res) => {
    res.render("products");
});


// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
        // return {validity: false, msg: "Server has issues, Please notify Alcoft"};
    })
}

/*
"Invalid password;"
"Restaurant ID doesn't exist;"
"Password ID not entered;"
"Restaurant ID not entered;"
"Restaurant ID or password is undefined;"
{validity: false, msg: }
*/
//getTableLengthsArrayF(cliRes[0].tablesData);



// Login;
app.post("/login", (req, res) => {
    validateUserF(req.body.restaurantID, req.body.password).then(resolved => {
        // console.log("gg");
        // console.log(resolved.clientData.tablesData.length);
        res.json({validity: true, restaurantID: resolved.clientData.restaurantID, password: resolved.clientData.password, userData: {tableFillStates: getTableLengthsArrayF(resolved.clientData.tablesData), tableCount: resolved.clientData.tableCount, takeAwayCount: resolved.clientData.takeAwayData.length}});
    }).catch(rejected => {
        console.log("ff");
        res.json({validity: false, msg: rejected.msg});
    });
});


const sendSingleTableData = (requestBody) => {
    let restaurantID = requestBody.restaurantID;
    let password = requestBody.password
    let tableIndex = requestBody.curTabIndex

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
            } else reject({validity: false, msg: "Restaurant ID not entered;"});
        } else reject({validity: false, msg: "Issues with the request;"});
    })
};


// Single Table Data;
app.post("/singleTableData", (req, res) => {
    sendSingleTableData(req.body).then(resolved => {
        console.log(resolved);
        res.json(resolved);
    }).catch(rejected => {
        console.log("ff");
        res.json({validity: false, msg: rejected.msg});
    });
});





// What did I learn:
// Template strings dont work in mongoose queries, you have to turn them to normal strings;
// For turning template strings to norml strings, you put square brackets around them: [` your string data `];
// DONT EVER FUCKING WASTE 3 HOURS ON THIS RETARDED FUCKING PROBLEM & LEARN A NEW DATABASE COZ MONGODB SUCKS (EVEN THO I LOVE IT, IT SUCKS.);

const setItemAsDeliveredF = async (args) => {
    await Client.updateOne({restaurantID: args.restaurantID}, 
        { [`tablesData.${args.curTabIndex}.tBill.${args.itemIndex}.d`]: true }, 
        { upsert: true }
    );
}

const deleteItemFromBillF = async (args) => {
    /**
     * Sadly, there is no way of deleting an array element by its index in mongoose.
     * After hours of wasting time, this is the only method I found which works;
     * Given an item index, 
     * the name of the item index is updated to "del" and then another database request queries objects from the desired location with the "del" name being searched;
     * When the del name is found, the object is then deleted;
     */    
    let itemData = await Client.findOneAndUpdate({restaurantID: args.restaurantID}, 
        { [`tablesData.${args.curTabIndex}.tBill.${args.itemIndex}.n`]: "del" }, 
        { upsert: true }
    );    
    console.log("=========================================");
    console.log(itemData);
    console.log("=========================================");        
    await Client.updateOne({restaurantID: args.restaurantID}, { 
        $pull: {
            // We have to specify "n"(name) as you can only pull from an array;
            // The bill items are also objects, so in the dot notation of the array we look into the "all tablebill"/"all items of the tablebill" of the table index;
            // and then if an object with the n being "del" is found, we pull it;
            [`tablesData.${args.curTabIndex}.tBill`]: {n: "del"}
        },
        // The value is removed from the array, decrementing the value now;
        $inc: {
            [`tablesData.${args.curTabIndex}.tbp`]: 0-(itemData.tablesData[args.curTabIndex].tBill[args.itemIndex].p * itemData.tablesData[args.curTabIndex].tBill[args.itemIndex].c)
        }
    
    }, { safe: true, upsert: true }
    );
        
    
    
}


const validateEditBillItemDataF = (requestBody) => {
    // Assigning the variables from the object;
    let restaurantID = requestBody.restaurantID;
    let password     = requestBody.password;
    let curTabIndex  = requestBody.curTabIndex;
    let itemIndex    = requestBody.itemIndex;
    let editStyle    = requestBody.editStyle;

    // Authenticating the data;
    return new Promise((resolve, reject) => {
        if (restaurantID != undefined && password != undefined && curTabIndex != undefined && itemIndex != undefined && editStyle != undefined && restaurantID != null && password != null && curTabIndex != null && itemIndex != null && editStyle != null) {
            if (restaurantID.length > 0) {
                if (password.length > 0) {
                    if (!isNaN(curTabIndex)) {
                        if (!isNaN(itemIndex)) {
                            if (editStyle.length > 0) {
                                // Basic auth succesfull;
                                // Checking the server now;
                                Client.find({restaurantID}).then(cliRes => {
                                    // Existence validation;
                                    if (cliRes.length > 0) {
                                        // Password authentication;
                                        if (cliRes[0].password == password) {
                                            // Table index authentication;
                                            if (cliRes[0].tablesData.length > curTabIndex) {
                                                // Item index validation;
                                                if (cliRes[0].tablesData[curTabIndex].tBill.length > itemIndex) {
                                                    // Checking if the item is delivered or not;
                                                    if (!cliRes[0].tablesData[curTabIndex].tBill[itemIndex].d) {
                                                        // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                        // Authentication succesfull, 
                                                        // setting the item values based off the request type;
                                                        if (editStyle == "deliver") {
                                                            // Setting the item as delivered;
                                                            setItemAsDeliveredF({restaurantID, curTabIndex, itemIndex});
                                                        } else {
                                                            // As the editStyle isn't "deliver", it's fair to asume its  "del", so deleting the item;
                                                            deleteItemFromBillF({restaurantID, curTabIndex, itemIndex});
                                                        }
                                                        // Resolving;
                                                        resolve();
                                                        // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    } else reject({validity: false, msg: "The item is already delivered;"});
                                                } else reject({validity: false, msg: "Invalid item index;"});
                                            } else reject({validity: false, msg: "Invalid table index;"});
                                        } else reject({validity: false, msg: "Invalid password;"});
                                    } else reject({validity: false, msg: "Restaurant ID doesn't exist;"});
                                }).then(err => console.log(err));
                                // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                            } else reject({validity: false, msg: "Please choose an editstyle;"});
                        } else reject({validity: false, msg: `Item index has to be an integer, not a ${typeof tableIndex}`})
                    } else reject({validity: false, msg: `Table index has to be an integer, not a ${typeof tableIndex}`})
                } else reject({validity: false, msg: "Password not entered;"});
            } else reject({validity: false, msg: "Restaurant ID not entered;"});
        } else reject({validity: false, msg: "Issues with the request;"});
    })

};


// Edit bill item data;
app.post('/editBillItemData', (req, res) => {
    validateEditBillItemDataF(req.body).then(resolved => {
        console.log("resovled");
        res.json({validity: true});
    }).catch(rejected => {
        res.json(rejected);
        console.log("rejected");
    });
});







const addItemToBillFACTUAL = async (args) => {
    // Creating the itemschema to put in the bill;
    console.log(args.itemData)
    let itemPrice = parseFloat(args.itemData[1]);
    let itemCount = parseFloat(args.itemData[2]);
    let item = {
        n: args.itemData[0],
        p: itemPrice,
        d: false,
        c: itemCount
    }
    console.log(item);

    await Client.updateOne({restaurantID: args.restaurantID}, 
        { $push: {
            [`tablesData.${args.curTabIndex}.tBill`]: item
        },
        // Item has been added to the array, incrementing the price now;
        $inc: {
            [`tablesData.${args.curTabIndex}.tbp`]: itemPrice*itemCount 
        }}, 
        { upsert: true }
    );
}


const addItemToBillF = (requestBody) => {
    // Assigning the variables from the object;
    let restaurantID = requestBody.rid;
    let password     = requestBody.p;
    let curTabIndex  = requestBody.cti;
    let itemData     = requestBody.itemd;
    let itemDataN = itemData[0]
    let itemDataP = itemData[1]
    let itemDataC = itemData[2]
    console.log("a");
    return new Promise((resolve, reject) => {
        if (restaurantID != undefined && password != undefined && curTabIndex != undefined && itemData != undefined && restaurantID != null && password != null && curTabIndex != null && itemData != null) {
            console.log(1);
            if (restaurantID.length > 0) {
                console.log(2);
                if (password.length > 0) {
                    console.log(3);
                    if (!isNaN(curTabIndex)) {
                        console.log(4);
                        console.log(itemData)
                        if (itemDataN != undefined && itemDataN.length > 0) {
                            console.log(6);
                            if (itemDataP != undefined && !isNaN(itemDataP)) {
                                if (itemDataC != undefined && !isNaN(itemDataC)) {
                                    // Basic authentication done, authenticating the user now;
                                    Client.find({restaurantID}).then(cliRes => {
                                        if (cliRes.length > 0) {
                                            if (cliRes[0].password == password) {
                                                // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                // Authentication Succesfull;
                                                // Adding the product to the bill now;
                                                console.log(itemData);
                                                addItemToBillFACTUAL({restaurantID, curTabIndex, itemData});

                                                // Resolving;
                                                resolve();
                                                // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                            } else reject({validity: false, msg: "Invalid password;"});
                                        } else reject({validity: false, msg: "Restaurant ID doesn't exist;"});
                                    }).catch(err => console.log(err));
                                } else reject({validity: false, msg: "Invalid count;"})
                            } else reject({validity: false, msg: "Invalid Price;"});
                        } else reject({validity: false, msg: "No item name;"});
                    } else reject({validity: false, msg: "No item data;"});
                } else reject({validity: false, msg: "Password not entered;"});
            } else reject({validity: false, msg: "Restaurant ID not entered;"});
        } else reject({validity: false, msg: "Issues with the request;"});
    })
};

// Add item to bill;
app.post('/addItemToBill', (req, res) => {
    console.log(req.body)
    addItemToBillF(req.body).then(resolved => {
        console.log(resolved);
        res.json({v: true});
    }).catch(rejected => {
        console.log(rejected);
        res.json({v: false});
    })
})

// The function for authenticating the transaction;
const authenticateTransactionF = ({restaurantID, password, tableIndex}) => {
    return new Promise((resolve, reject) => {
        if (restaurantID != undefined && password != undefined && restaurantID != null && password != null && tableIndex != undefined && tableIndex != null) {
            if (restaurantID.length > 0) {
                if (password.length > 0) {
                    if (!isNaN(tableIndex)) {
                        Client.find({restaurantID}).then(cliRes => {
                            if (cliRes.length > 0) {
                                if (cliRes[0].tablesData.length > tableIndex && cliRes[0].tablesData[tableIndex] != undefined && cliRes[0].tablesData[tableIndex] != null) {
                                    if (cliRes[0].password == password) {
                                        // Checking if there are any products on the bill at all;
                                        if (cliRes[0].tablesData[tableIndex].tBill.length > 0) {
                                            // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                            // ~~~~~~~~~~~~~~~~~ Authentication Successfull ~~~~~~~~~~~~~~~~~
                                            console.log("Succesuflul Transaction Authentication!");
                                            resolve();
                                        } else reject({validity: false, msg: "No products in the bill;"});
                                    } else reject({validity: false, msg: "Invalid password;"});
                                } else reject({validity: false, msg: "Invalid table id;"});
                            } else reject({validity: false, msg: "Restaurant ID doesn't exist;"});
                        }).catch(err => console.log(err));
                    } else reject({validity: false, msg: `Table index has to be an integer, not a ${typeof tableIndex}`})
                } else reject({validity: false, msg: "Password not entered;"});
            } else reject({validity: false, msg: "Restaurant ID not entered;"});
        } else reject({validity: false, msg: "Issues with the request;"});
    })
};

const doTransactionFActual = async ({restaurantID, password, tableIndex}) => {
    await Client.updateOne({restaurantID}, {
        $set: {
            [`tablesData.${tableIndex}.tBill`]: [],
            [`tablesData.${tableIndex}.tbp`]: 0
        }
    })
};


// Do Transaction;
app.post("/doTransaction", (req, res) => {
    let restaurantID = req.body.restaurantID;
    let password = req.body.password
    let tableIndex = req.body.curTabIndex

    authenticateTransactionF({restaurantID, password, tableIndex}).then(() => {
        // Authentication has succeeded, doing the transaction now;
        console.log("gg");
        // Doing it;
        doTransactionFActual({restaurantID, password, tableIndex});

        // Responding;
        res.json({validity: true});
        // NOTE: No values were returned from the server as the client will already fetch the bill data first;

    }).catch(rejected => res.json(rejected));
})



const deleteSaleValidityF = (requestBody) => {
    let restaurantID = requestBody.restaurantID;
    let password = requestBody.password
    let tableIndex = requestBody.curTabIndex

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
                                        resolve(); // Resolving;
                                    } else reject();
                                } else reject();
                            } else reject();
                        }).catch(err => console.log(err));
                    } else reject()
                } else reject();
            } else reject();
        } else reject();
    })
}


// Delete sale;
app.post("/delSale", (req, res) => {
    let restaurantID = req.body.restaurantID;
    let password = req.body.password
    let tableIndex = req.body.curTabIndex
    deleteSaleValidityF(req.body).then(() => {
        doTransactionFActual({restaurantID, password, tableIndex})
        res.json({validity: true});
    }).catch(() => {
        res.json({validity: false});
    })
})



// 404 Page;
app.use((req, res) => {
    res.send("<h1>404, Page not found</h1>");
})


