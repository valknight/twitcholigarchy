function get_id(callback) {
    fetch('/api/user')
        .then(response => response.json())
        .then(data => callback(data));
}

function get_poll(callback) {
    fetch('/api/poll')
        .then(response => response.json())
        .then(data => callback(data));
}

get_id(function(data) {
    document.getElementById("username").innerHTML = data.display_name;
    document.getElementById("userid").innerHTML = data.id;
})

function update_poll() {
    get_poll(function(data) {
        if (data.hasOwnProperty('message')) {
            if ("no active poll".match(data.message)) {
                document.getElementById("mainContainer").style.display = "none";
                return;
            }
        }
        document.getElementById("mainContainer").style.display = "inherit";
        document.getElementById("pollname").innerHTML = data.name;
        document.getElementById("blueteam").innerHTML = data.blueteam.name;
        document.getElementById("redvotes").innerHTML = data.blueteam.votes;
        document.getElementById("pinkteam").innerHTML = data.pinkTeam.name;
        document.getElementById("pinkvotes").innerHTML = data.pinkTeam.votes;
        let redWidth = (100 / (data.blueteam.votes + data.pinkTeam.votes)) * data.blueteam.votes;
        if (Number.isNaN(redWidth)) {
            redWidth = 50;
        }
        console.log(redWidth);
        document.getElementById("bluebar").style.width = redWidth + "%";
        document.getElementById("pinkbar").style.width = (100 - redWidth) + "%";
        if (data.isOpen) {
            document.getElementById("pollbox").style.backgroundColor = "darkolivegreen";
            document.getElementById("runningStatus").innerHTML = "Open!";
        } else {
            document.getElementById("pollbox").style.backgroundColor = "darkslategrey"
            document.getElementById("runningStatus").innerHTML = "Poll closed!";
        }
        if (redWidth == 100 || redWidth == 0) {
            document.getElementById("bluebar").style.borderTopRightRadius = "5px";
            document.getElementById("bluebar").style.borderBottomRightRadius = "5px";
            document.getElementById("pinkbar").style.borderTopLeftRadius = "5px";
            document.getElementById("pinkbar").style.borderBottomLeftRadius = "5px";
        } else {
            document.getElementById("bluebar").style.borderTopRightRadius = "0px";
            document.getElementById("bluebar").style.borderBottomRightRadius = "0px";
            document.getElementById("pinkbar").style.borderTopLeftRadius = "0px";
            document.getElementById("pinkbar").style.borderBottomLeftRadius = "0px";
        }
    })
}

time_poller = setInterval(update_poll, 1000)