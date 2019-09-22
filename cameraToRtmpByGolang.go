package main

import (
	"fmt"
	"gocv.io/x/gocv"
	"log"
	"os"
	"os/exec"
	"os/signal"
	"strings"
	//"syscall"
)

func main() {
	//signal.Ignore(syscall.SIGPIPE)
	signal.Ignore()

	// set to use a video capture device 0
	//deviceID := 0
	deviceID := "rtsp://192.168.0.10/live/live0"

	// open webcam
	webcam, err := gocv.OpenVideoCapture(deviceID)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer webcam.Close()
	fmt.Println("open cam ok")

	// open display window
	window := gocv.NewWindow("Face Detect")
	defer window.Close()
	fmt.Println("NewWindow ok")

	// prepare image matrix
	img := gocv.NewMat()
	defer img.Close()

	//for ffmpeg push to rtmp server
	cmdargs := "ffmpeg -y -an -f rawvideo" +
		" -vcodec rawvideo -pix_fmt bgr24" +
		" -s 1280x720 -r 25 -i - -c:v libx264" +
		" -pix_fmt yuv420p -preset ultrafast -f flv" +
		" rtmp://192.168.0.30:1935/live/movie"
	list := strings.Split(cmdargs, " ")
	cmd := exec.Command(list[0], list[1:]...)
	cmdIn, err := cmd.StdinPipe()
	if err != nil {
		log.Fatal(err)
	}
	defer cmdIn.Close()
	if err := cmd.Start(); err != nil {
		log.Fatal(err)
	}

	fmt.Printf("start reading camera device: %v\n", deviceID)
	for {
		if ok := webcam.Read(&img); !ok {
			fmt.Printf("cannot read device %v\n", deviceID)
			return
		}
		if img.Empty() {
			continue
		}
		fmt.Println("read frame ok")

		// show the image in the window, and wait 1 millisecond
		window.IMShow(img)
		window.WaitKey(1)

		//push to rtmp server
		cnt,err :=cmdIn.Write([]byte(img.ToBytes()))
		//cnt,err :=cmdIn.Write(img.ToBytes())
		if err !=nil {
			fmt.Printf("%v",err)
			os.Exit(0)
		}else{
			fmt.Printf("send cnt=%d\n",cnt)
		}
	}
}
