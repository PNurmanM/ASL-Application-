import Webcam from "react-webcam";
import {useRef, useState, useCallback, useEffect} from "react";
import {io} from "socket.io-client";

function WebcamComp(){

    
    const[socket, setSocket] = useState(null)
    const[imageName, setImageName] = useState("")
    const[prediction, setPrediction] = useState("N/A")


    useEffect(() => {
        const Nsocket = io("http://127.0.0.1:5000/")
        setSocket(Nsocket)

        return() => {
            Nsocket.close()
        }
    }, [])

    const webcamRef = useRef(null)

    const capture = useCallback(() => {
        const imageSrc = webcamRef.current.getScreenshot()
        console.log(imageSrc)
    },[webcamRef])

    const captureSend = async(e) => {
        e.preventDefault()

        const imageFile = webcamRef.current.getScreenshot()
        //const convertedImage = await fetch(imageFile).then(src => src.blob())
        
        socket.emit("send_image", {image_file: imageFile})

    }

    function updateName(e){
        setImageName(e.target.value);
    }

    useEffect(() => {

        if(!socket) return
        
        socket.on("prediction", (data) => {
            setPrediction(data.result)
        })

        return () => {
            socket.off("prediction")
        }
    }, [socket]);

    return (
        <>
            <Webcam
                ref={webcamRef} 
                screenshotFormat="image/jpeg"
                style={{width: "100%", maxWidth: "600px", borderRadius: "10px"}}
            />
            <input onChange={(e) => updateName(e)}></input>
            <button onClick={captureSend}>Take a Photo!</button>
            <p>Prediction: {prediction}</p>
        </>
    );
}

export default WebcamComp