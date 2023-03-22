"use strict"
const { createClient } = require("icqq")

const account = 0
const password = ''
const client = createClient({platform:5})

client.on('system.login.slider', (e) => {
  console.log('输入滑块地址获取的ticket后继续。\n滑块地址:\n' + e.url)
  process.stdin.once('data', (data) => {
      client.submitSlider(data.toString().trim())
  })
})

client.on('system.login.qrcode', (e) => {
  console.log('扫码完成后回车继续:    ')
  process.stdin.once('data', () => {
      client.login()
  })
})

client.on('system.login.device', (e) => {
  console.log('请选择验证方式:(1:短信验证 其他:扫码验证)')
  process.stdin.once('data', (data) => {
      if (data.toString().trim() === '1') {
          client.sendSmsCode()
          console.log('请输入手机收到的短信验证码:')
          process.stdin.once('data', (res) => {
              client.submitSmsCode(res.toString().trim())
          })
      } else {
          console.log('扫码完成后回车继续:' + e.url)
          process.stdin.once('data', () => {
              client.login()
          })
      }
  })
})

client.login(account, password)

exports.client = client

require("./plugins/hello")
require("./plugins/online")
