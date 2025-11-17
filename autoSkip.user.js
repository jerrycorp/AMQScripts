// ==UserScript==
// @name         AMQ Song skipper
// @namespace    https://github.com/jerrycorp
// @version      0.2
// @description  Skips songs automatically
// @author       jerrycorp
// @match        https://animemusicquiz.com/*
// @grant        none
// @downloadURL  https://github.com/jerrycorp/AMQScripts/raw/main/autoSkip.user.js
// @updateURL    https://github.com/jerrycorp/AMQScripts/raw/main/autoSkip.user.js
// @require      https://raw.githubusercontent.com/joske2865/AMQ-Scripts/main/common/amqScriptInfo.js
// ==/UserScript==

let active_interval = null;

function key_up_fun(event) {
	// noinspection EqualityComparisonWithCoercionJS
    if(event.altKey && event.keyCode=='84') {
        if (active_interval != null) {
            clearInterval(active_interval);
            active_interval = null;
            // noinspection JSUnresolvedReference
            gameChat.systemMessage("Disabled auto skip");
        } else {
            active_interval = setInterval(function() {
                skip()
             }, 2000);
            // noinspection JSUnresolvedReference
            gameChat.systemMessage("Enabled auto skip");
        }
	}
}
document.addEventListener('keyup', key_up_fun, false);

// noinspection JSUnresolvedReference
if (typeof Listener === "undefined") { // noinspection JSAnnotator
    return;
}

function active_players() {
    let count = 0
    for (key of Object.keys(quiz.players)) {
        if (!quiz.players[key].avatarSlot._disabled) count++;
    }
    return count;
}

function skip() {
    // noinspection EqualityComparisonWithCoercionJS
    if (viewChanger.currentView != "quiz") {
        return
    }

    if(active_players() < 2) {
        return
    }

    if (!document.querySelector("#qpInputSkipContainer.toggled")) {
        // noinspection JSUnresolvedReference
        quiz.skipClicked();
        document.querySelector("#qpInputSkipContainer").classList.add("highlight");
    }
}

new Listener("Join Game", (response) => {
	if(response.error) return;
	print_help();
}).bindListener();

new Listener("Spectate Game", (response) => {
	if(response.error) return;
	print_help();
}).bindListener();

function print_help() {
    gameChat.systemMessage("Press ALT+T to toggle auto skip");
}

// noinspection JSUnresolvedReference
AMQ_addScriptData({
    name: "Song Skipper",
    author: "jerrycorp",
    version: "0.1",
    link: "https://github.com/jerrycorp/AMQScripts/raw/main/autoSkip.user.js",
    description: `
        <p>Adds an option to skip songs automatically. Only use when other people</p>
        <p>are also playing without this script. Use ALT+T to toggle on/off.</p>
    `
});