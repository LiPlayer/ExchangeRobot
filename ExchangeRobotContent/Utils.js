.pragma library

function getCountdown(timestamp) {
    const pad = function(value) {
        return value < 10 ? "0" + value : value;
    }
    var currentTime = new Date().getTime(); // Current time in milliseconds
    var timeDiff = timestamp - currentTime; // Time difference in milliseconds

    if (timeDiff <= 0) {
        let countdown = "00:00:00"; // If time is up, return 00:00:00
        return countdown;
    }

    var days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
    var hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);

    // Format as 'days hh:mm:ss'
    var countdown;
    if (days === 0) {
        countdown = pad(hours) + ":" + pad(minutes) + ":" + pad(seconds);
    } else {
        countdown = days + "D " + pad(hours) + ":" + pad(minutes) + ":" + pad(seconds);
    }

    return countdown;
}
