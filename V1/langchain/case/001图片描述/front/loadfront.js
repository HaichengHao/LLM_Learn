const http = require('http')
const server = http.createServer()


server.on('request',(req,res)=>{

    res.setHeader('Content-Type','text/plain;charset=utf-8')
    res.end('hello , It\'s Welcomed to create u Web Server via node.js ')

})

server.listen(3000,()=>{
    console.log('web 服务已经启动')
})


