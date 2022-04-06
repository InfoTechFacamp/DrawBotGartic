/*
document.getElementById("draw").addEventListener("click", ()=>{
  let imageurl = document.getElementById("imageurl").value
  let colorpalete = document.getElementById("colorpalete").value
  let pencil = document.getElementById("pencil").value
  let colorpicker = document.getElementById("colorpicker").value
  let brightpicker = document.getElementById("brightpicker").value
  let conversion = document.getElementById("conversion").value
  eel.drawImage(imageurl, colorpalete, pencil, colorpicker, brightpicker, conversion)
}, false);
*/
eel.init()
async function draw() {
  let imageurl = document.getElementById("imageurl").value
  let conversion = document.getElementById("conversion").value
  let xsize = document.getElementById("xsize").value
  let ysize = document.getElementById("ysize").value
  let skipWhite = document.getElementById("pularbranco").checked
  let drawarea = document.getElementById("drawarea").checked
  let clicktime = document.getElementById("clicktime").value
  let numberofcolors = document.getElementById("numberofcolors").value
  let pixelgap = document.getElementById("pixelgap").value
  if (skipWhite === true) {
    skipWhite = 1
  } else {
    skipWhite = 0
  }
  if (drawarea === true) {
    drawarea = 1
  } else {
    drawarea = 0
  }
  eel.drawImage(imageurl, conversion, xsize, ysize, skipWhite, drawarea, clicktime, numberofcolors, pixelgap)
}

async function config() {
  eel.setarConfig()
}

eel.expose(prompt_alerts);
function prompt_alerts(description) {
  alert(description);
}

eel.expose(setLogText);
function setLogText(text) {
  document.getElementById("log").value = document.getElementById("log").value + text
}

eel.expose(apagarLog);
function apagarLog() {
  document.getElementById("log").value = ""
}

eel.expose(setTextBox)
function setTextBox(box,text) {
  document.getElementById(box).value = text
}

eel.expose(setCheckBox)
function setCheckBox(box,value) {
  Boolean(value.toLowerCase())
  document.getElementById(box).checked = value
}

eel.expose(getCheckBox)
function getCheckBox(box) {
  if (document.getElementById(box).checked === true) {
    return 1
  } else {
    return 0
  }
}

document.getElementById("draw").addEventListener("click", ()=>{
  draw()
})
document.getElementById("config").addEventListener("click", ()=>{
  config()
})