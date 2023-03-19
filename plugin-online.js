"use strict"
const { client } = require("./index")

client.on("system.online", function () {
    console.log(`我是${this.nickname}(${this.uin})，我有${this.fl.size}个好友，${this.gl.size}个群`)
})
