const mongoose = require("mongoose");
const Schema = mongoose.Schema;

const ClientSchema = new Schema({
    restaurantID: {
        type: String,
        required: true
    },
    password: {
        type: String,
        required: true
    },
    tablesData: {
        type: Array,
        required: false
    },
    takeAwayData: {
        type: Array,
        required: false
    },
    tableCount: {
        type: Number,
        required: true
    },
    takeAwayCount: {
        type: Number,
        required: true
    }

})


let Client = mongoose.model("client", ClientSchema);
module.exports = Client;