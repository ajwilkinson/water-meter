const request = require('request');
const Gpio = require('onoff').Gpio;

const sensor = new Gpio(2, 'in', 'both', {
    debounceTimeout: 50
});

const payload = "water,location=Home used=10";

const url="http://workshop.local:8086/write?db=water";

sensor.watch((err, value) => {
    if (err) {
        return;
    }
    if (value===0) {
        request({
            url:url,
            method: "POST",
            body:payload    
        }, (error, response) => {
            if (error) 
                console.log(error);
        })
    }
})

console.log("water-meter ready");


