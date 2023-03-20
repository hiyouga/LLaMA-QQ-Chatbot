"use strict"
const needle = require("needle")
const { client } = require("./index")

// send private messages
client.on("message.private", function (msg) {
    if (msg.raw_message === "/help") {
        msg.reply("/preset [default/assistant/nekogirl/imotto] 使用预设 /prompt 吟唱咒语 /clear 清空记忆", false) // false: turn off quote
    } else {
        var nested = {
            msg: msg.raw_message
        }
        needle.post("http://127.0.0.1:5000/msg", nested, function(error, response) {
            if (!error && response.statusCode == 200) {
                msg.reply(response.body, false)
            } else {
                console.log(response.statusCode)
                console.log(response.body)
            }
        })
    }
})

// send group messages
client.on("message.group", function (msg) {
    if (msg.raw_message.search("@小冰") != -1) {
        if (msg.raw_message.search("/help") != -1) {
            msg.reply("/preset [default/assistant/nekogirl/imotto] 使用预设 /prompt 吟唱咒语 /clear 清空记忆", false)
        } else {
            var nested = {
                msg: msg.raw_message.replace("@小冰", "")
            }
            needle.post("http://127.0.0.1:5000/msg", nested, function(error, response) {
                if (!error && response.statusCode == 200) {
                    msg.reply(response.body, false)
                } else {
                    console.log(response.statusCode)
                    console.log(response.body)
                }
            })
        }
    }
})

// receive poke notice
client.on("notice.group.poke", function (e) {
    if (e.target_id === this.uin) {
        e.group.sendMsg("不许戳戳，会坏掉的喵~")
    }
})
