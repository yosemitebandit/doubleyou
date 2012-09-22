function sketchProc(processing) {
    processing.draw = function() {
        var centerX = processing.width / 2; 
        var centerY = processing.height / 2;
        var maxArmLength = Math.min(centerX, centerY);

        function drawArm(position, lengthScale, weight) {
            processing.strokeWeight(weight);
            processing.line(centerX, centerY, 
                centerX + Math.sin(position * 2 * Math.PI) * lengthScale * maxArmLength,
                centerY - Math.cos(position * 2 * Math.PI) * lengthScale * maxArmLength);
        }

        processing.background(224);

        var now = new Date();

        var hoursPosition = (now.getHours() % 12 + now.getMinutes() / 60) / 12;
        drawArm(hoursPosition, 0.5, 5);
    }
}

var canvas = document.getElementById('doubleyou-avatar');

var processingInstance = new Processing(canvas, sketchProc);