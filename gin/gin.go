package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
)

func main() {
	router := gin.Default()

	router.LoadHTMLFiles("index.html")
	router.StaticFS("/strobe", http.Dir("./strobe"))
	router.StaticFS("/favicon.ico", http.Dir("./favicon"))
	router.GET("/", func(c *gin.Context) {
		c.HTML(http.StatusOK, "index.html", gin.H{
		})
	})


	router.Run("192.168.0.107:8080")
}
