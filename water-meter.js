const request = require('request');
const Gpio = require('onoff').Gpio;

const sensor = new Gpio(2, 'in', 'both', {
    debounceTimeout: 50
});

const payload = "water,location=Home used=10";

const url="http://192.168.1.20:8086/write?db=water";

sensor.watch((err, value) => {
    if (err) {
        console.log(err);
        return;
    }
    console.log(value);
    if (value===0) {
        request({
            url:url,
            method: "POST",
            body:payload    
        }, (error, response) => {
            if (error) 
                console.log(error);
            else 
                console.log(response.statusCode);
        })
    }
})

console.log("Ready...");


