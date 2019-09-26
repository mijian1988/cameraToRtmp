package main

import (
	"fmt"
	"gocv.io/x/gocv"
	"log"
	"os"
	"os/exec"
	"os/signal"
	"strings"
)

func main() {
	//signal.Ignore(syscall.SIGPIPE)
	signal.Ignore()

	// set to use a video capture device 0
	deviceID := 0
	//deviceID := "rtsp://192.168.0.30/live/live0"

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
	width := int(webcam.Get(gocv.VideoCaptureFrameWidth))
	height := int(webcam.Get(gocv.VideoCaptureFrameHeight))
	fps := int(webcam.Get(gocv.VideoCaptureFPS))

	cmdArgs :=fmt.Sprintf("%s %s %s %d %s %s",
		"ffmpeg -y -an -f rawvideo -vcodec rawvideo -pix_fmt bgr24 -s",
		fmt.Sprintf("%dx%d", width, height),
		"-r",
		fps,
		"-i - -c:v libx264 -pix_fmt yuv420p -preset ultrafast -f flv",
		"rtmp://192.168.0.30:1935/live/movie",
		)
	fmt.Printf("cmdargs:%s\n",cmdArgs)
	list := strings.Split(cmdArgs, " ")
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

		// show the image in the window, and wait 1 millisecond
		window.IMShow(img)
		window.WaitKey(1)

		//push to rtmp server
		_,err :=cmdIn.Write([]byte(img.ToBytes()))
		if err !=nil {
			fmt.Printf("%v",err)
			os.Exit(0)
		}
	}
}
