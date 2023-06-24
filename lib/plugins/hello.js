"use strict"
const { Configuration, OpenAIApi } = require("openai")
const { client } = require("./../bot")

const configuration = new Configuration({
    basePath: "http://192.168.5.193:8000/v1",
    apiKey: "123456789"
});
const openai = new OpenAIApi(configuration);

var history = new Array();
var currentLen = 0;
const maxLen = 1024;

async function responseMsg(msg, nickname) {
    if (msg.raw_message.search("/help") != -1) {
        msg.reply("/clear 清空记忆", false);
    } else if (msg.raw_message.search("/clear") != -1) {
        history = new Array();
        currentLen = 0;
        msg.reply("[记忆清空完成]", false);
    } else {
        var query = msg.raw_message.replace(nickname, "").trim();
        var messages = history.concat(new Array({role: "user", content: query}));

        const chatCompletion = await openai.createChatCompletion({
            model: "default",
            messages: messages
        });
        var response = chatCompletion.data.choices[0].message.content;

        msg.reply(response, false);
        history.push({role: "user", content: query}, {role: "assistant", content: response})
        currentLen = currentLen + query.length + response.length;

        while (currentLen > maxLen) {
            garbage_query = history.shift();
            garbage_response = history.shift();
            currentLen = currentLen - garbage_query.content.length - garbage_response.content.length;
        }
    }
}

// send private messages
client.on("message.private", function (msg) {
    try {
        responseMsg(msg, "@" + this.nickname);
    } catch (error) {
        console.log(error);
    }
})

// send group messages
client.on("message.group", function (msg) {
    try {
        if (msg.raw_message.search("@" + this.nickname) != -1) {
            responseMsg(msg, "@" + this.nickname);
        }
    } catch (error) {
        console.log(error);
    }
})

// receive poke notice
client.on("notice.group.poke", function (e) {
    if (e.target_id === this.uin) {
        e.group.sendMsg("不许戳戳，会坏掉的喵~")
    }
})
