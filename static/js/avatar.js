// ENUMS
var COLORS = {
    PINK: 1,
    GREEN: 2,
    YELLOW: 3,
    BLUE: 4,
    ORANGE: 5
};

var BAD = 1;
var OKAY = 2;
var GOOD = 3;

// GENERAL FUNCTIONS
var polarToCart = function(r, deg) {
    var dx = r * Math.cos(deg);
    var dy = r * Math.sin(deg);
    return [dx, dy];
};

var inRange = function(val, min, max) {
    if (val >= min && val <= max) {
        return true;
    }
    return false;
};

var lineEq = function (m, p, b) {
    return m * p + b;
};

// DRAWING AND UI

function sketchProc(processing) {
    window.proc = processing;

    proc.width = 600;
    proc.height = 400;
    // proc.ellipseMode(proc.CENTER);

    var background = function(a, b, c, d) {
        return proc.background(a, b, c, d);
    };
    var fill = function(a, b, c, d) {
        return proc.fill(a, b, c, d);
    };
    var stroke = function(a, b, c, d) {
        return proc.stroke(a, b, c, d);
    };
    var noStroke = function() {
        return proc.noStroke();
    };
    var strokeWeight = function(a) {
        return proc.strokeWeight(a);
    };
    var triangle = function(a, b, c, d, e, f) {
        return proc.triangle(a, b, c, d, e, f);
    };
    var ellipse = function(a, b, c, d) {
        return proc.ellipse(a, b, c, d);
    };
    var quad = function(a, b, c, d, e, f, g, h) {
        return proc.quad(a, b, c, d, e, f, g, h);
    };
    var arc = function(a, b, c, d, e, f) {
        return proc.arc(a, b, c, d, e * Math.PI/180, f * Math.PI/180);
    };
    var random = function(a, b) {
        return proc.random(a, b);
    };
    var floor = function(a) {
        return proc.floor(a);
    };
    var size = function(a, b) {
        return proc.size(a, b);
    };

    var avatar = function(options) {
        this.setParams = function(options) {
            this.x = options.x || this.x;
            this.y = options.y || this.y;
            this.r = options.r || this.r;
            this.color = options.color || this.color;
            this.mood = options.mood || this.mood;
            this.sleep = options.sleep || this.sleep;
            this.nutrition = options.nutrition || this.nutrition;
            this.activity = options.activity || this.activity;
        };

        this.setParams(options);

        this.bodyFill = function() {
            if (this.color === COLORS.PINK) {
                fill(219, 57, 57);
            } else if (this.color === COLORS.GREEN) {
                fill(156, 204, 79);
            } else if (this.color === COLORS.YELLOW) {
                fill(255, 205, 5);
            } else if (this.color === COLORS.BLUE) {
                fill(120, 205, 245);
            } else if (this.color === COLORS.ORANGE) {
                fill(235, 180, 117);
            }
        };

        this.bodyStroke = function() {
            if (this.color === COLORS.PINK) {
                stroke(214, 141, 141);
            } else if (this.color === COLORS.GREEN) {
                stroke(119, 186, 131);
            } else if (this.color === COLORS.YELLOW) {
                stroke(204, 186, 98);
            } else if (this.color === COLORS.BLUE) {
                stroke(72, 175, 240);
            } else if (this.color === COLORS.ORANGE) {
                stroke(224, 143, 56);
            }
        };

        this.drawTriangle = function(d1, d2, d3, isLeft) {
            var m = isLeft ? -1 : 1;
            var x1 = this.x + m * d1[0];
            var x2 = this.x + m * d2[0];
            var x3 = this.x + m * d3[0];
            var y1 = this.y - d1[1];
            var y2 = this.y - d2[1];
            var y3 = this.y - d3[1];
            triangle(x1, y1, x2, y2, x3, y3);
        };

        this.drawTriangles = function(m1, m2, m3, t1, t2, t3) {
            var d1 = polarToCart(this.r * m1, t1);
            var d2 = polarToCart(this.r * m2, t2);
            var d3 = polarToCart(this.r * m3, t3);
            noStroke();
            // left
            this.drawTriangle(d1, d2, d3, true);
            // right
            this.drawTriangle(d1, d2, d3, false);
        };

        this.drawEars = function() {
            this.drawTriangles(0.95, 0.95, 1.2, 30, 70, 70);
    //        this.drawTriangles(0.95, 0.95, 1.2, 10, 60, 20);
        };

        this.drawLegs = function() {
            this.drawTriangles(0.95, 0.95, 1.2, -30, -70, -70);
        };

        this.drawArms = function(t1, t2, t3) {
            this.drawTriangles(0.95, 0.95, 1.3, t1, t2, t3);
        };

        this.drawBody = function() {
            this.bodyFill();
            this.bodyStroke();
            strokeWeight(this.r/10);
            ellipse(this.x, this.y, this.r*2, this.r*2);
        };

        this.smallSmile = function() {
            arc(this.x, this.y, this.r/5, this.r/5, 60, 120);
        };

        this.sadSmile = function(){
            arc(this.x, this.y + this.r/3, this.r/2, this.r/4, 240, 300);
        };

        this.medSmile = function() {
            arc(this.x, this.y, this.r/2, this.r/4, 60, 120);
        };

        this.bigSmile = function() {
            arc(this.x, this.y, this.r/2, this.r/4, 40, 140);
        };

        this.drawSmile = function() {
            this.bodyFill();
            stroke(0, 0, 0);
            strokeWeight(this.r/25);

            if (this.mood === BAD) {
                this.sadSmile();
            } else if (this.mood === OKAY) {
                this.medSmile();
            } else if (this.mood === GOOD) {
                this.bigSmile();
            }
        };

        this.sadEye = function(a, b) {
            this.bodyFill();
            arc(a, b, this.r/5, this.r/5, 40, 140);
        };

        this.okayEye = function(a, b) {
            fill(0, 0, 0);
            ellipse(a, b, this.r/10, this.r/10);
        };

        this.happyEye = function(a, b) {
            this.bodyFill();
            arc(a, b, this.r/5, this.r/5, 220, 320);
        };

        this.drawEyes = function() {
            stroke(0, 0, 0);
            strokeWeight(this.r/25);

            var dx = this.r/2;
            var dy = -this.r/10;
            var x1 = this.x - dx;
            var x2 = this.x + dx;
            var y1 = this.y + dy;

            if (this.mood === BAD) {
                this.sadEye(x1, y1 + this.r/20);
                this.sadEye(x2, y1 + this.r/20);
            } else if (this.mood === OKAY) {
                this.okayEye(x1, y1, 10);
                this.okayEye(x2, y1, 10);
            } else if (this.mood === GOOD) {
                this.happyEye(x1, y1 + this.r/20);
                this.happyEye(x2, y1 + this.r/20);
            }
        };

        this.moveArms = function() {
            if (frameCount % 60 < 15) {
                this.drawArms(-10, 5, 10);
            } else if (inRange(frameCount % 60, 15, 30)) {
                this.drawArms(-10, 5, 5);
            } else if (frameCount % 60 > 30) {
                this.drawArms(-10, 5, 0);
            }
        };

        // SKY (SLEEP)
        var randomX = [];
        var randomY = [];
        var randomSize = [];

        this.prepClouds = function() {
            for (var i = 0; i < 20; i += 1) {
                randomX.push(random(-this.r, this.r));
                randomY.push(random(-3 * this.r, -2 * this.r));
                randomSize.push(random(this.r, this.r * 2));
            }
        };

        this.drawClouds = function(shade) {
            fill(shade, shade, shade, 60);
            for (var i = 0, j = randomX.length; i < j; i += 1) {
                var shiftX = randomX[i];
                var shiftY = randomY[i];
                var size = randomSize[i];
                ellipse(this.x + shiftX, this.y + shiftY, size, size * 0.8);
            }
        };

        this.drawSun = function() {
            fill(255, 247, 92);
            var shiftX = randomX[0];
            var shiftY = randomY[0];
            ellipse(this.x + shiftX, this.y + shiftY, this.r, this.r);
            fill(255, 237, 43, 100);
            ellipse(this.x + shiftX, this.y + shiftY, this.r*1.7, this.r*1.7);
        };

        this.drawSky = function() {
            noStroke();
            if (this.sleep === BAD) {
                this.drawClouds(130);
            } else if (this.sleep === OKAY) {
                this.drawClouds(255);
            } else if (this.sleep === GOOD) {
                this.drawSun();
            }
        };

        // PLANT (NUTRITION)


        // ROAD (ACTIVITY)
        this.drawRoadBackground = function() {
            fill(87, 87, 87);
            var dx1 = this.r/6;
            var dx2 = 3 * this.r/2;
            var dy = 2 * this.r;
            var x1 = this.x - dx1;
            var x2 = this.x + dx1;
            var x3 = this.x + dx2;
            var x4 = this.x - dx2;
            var y1 = this.y;
            var y2 = this.y;
            var y3 = this.y + dy;
            var y4 = this.y + dy;
            quad(x1, y1, x2, y2, x3, y3, x4, y4);
        };

        this.drawRoadLine = function(p1, p2) {
            fill(255, 212, 125);
            var x1 = this.r/24;
            var x2 = this.r/8;
            var y1 = this.r;
            var y2 = this.r * 3;
            var dx = x2 - x1;
            var dy = y2 - y1;
            var xc1 = dx * p1;
            var xc2 = dx * p2;
            var eq1 = lineEq(dy, p1, this.y);
            var eq2 = lineEq(dy, p2, this.y);
            quad(this.x + xc1, eq1, this.x + xc2, eq2, this.x - xc2, eq2, this.x - xc1, eq1);
        };

        this.drawRoadLines = function(markers) {
            var j = floor(markers.length/2);
            for (var i = 0; i < j; i += 1) {
                this.drawRoadLine(markers[i*2], markers[i*2+1]);
            }
        };

        this.drawRoad = function() {
            noStroke();
            this.drawRoadBackground();
            var mod = 10 * this.activity;
            var modval = frameCount % mod;
            if (modval < floor(mod/3)) {
                this.drawRoadLines([0.5, 0.6, 0.7, 0.8, 0.9, 1]);
            } else if (inRange(modval, floor(mod/3), floor(mod*2/3))) {
                this.drawRoadLines([0.45, 0.55, 0.65, 0.75, 0.85, 0.95]);
            } else {
                this.drawRoadLines([0.4, 0.5, 0.6, 0.7, 0.8, 0.9]);
            }

        };

        this.render = function() {
            this.drawRoad();
            this.drawBody();
            this.drawEars();
            this.drawLegs();
            this.moveArms();

            this.drawEyes();
            this.drawSmile();

            this.drawSky();

            return this;
        };

        this.prepClouds();
        return this;
    };

    var y = 200;
    var r = 50;
    var a1 = new avatar({
        x: 100,
        y: 200,
        r: 40,
        color: COLORS.PINK,
        mood: OKAY,
        sleep: OKAY,
        nutrition: OKAY,
        activity: OKAY

    });

    var a2 = new avatar({
        x: 300,
        y: 250,
        r: 60,
        color: COLORS.GREEN,
        mood: BAD,
        sleep: BAD,
        nutrition: BAD,
        activity: BAD
    });

    var a3 = new avatar({
        x: 500,
        y: 200,
        r: 40,
        color: COLORS.BLUE,
        mood: GOOD,
        sleep: GOOD,
        nutrition: GOOD,
        activity: GOOD
    });

    var frameCount = 0;

    var updateAvatar = function(data) {
        var activity = data.physical_activity;
        // var mood = data.question_responses;
        var nutrition = data.net_calories;
        var sleep = data.time_slept;

        
        var mood = Math.round(data.total_score/33);

        a2.setParams({
            "mood": mood,
            "sleep": sleep,
            "nutrition": nutrition,
            "activity": activity
        });
    };
    
    days_ago = 0;

    processing.draw = function() {
        background(189, 226, 255);
        a1.render();
        a2.render();
        a3.render();
        frameCount += 1;

        if (frameCount % 100 === 0) {

            var date = (days_ago).days().ago();
            
            var month = date.getMonth();
            if (month == 0) {
                month = 1;
            }
            if (month < 10) {
                month = '0' + month;
            } else {
                month = month + '';
            }

            var d = date.getDay();
            if (d == 0) {
                d = 1;
            }
            if (d < 10) {
                d = '0' + d;
            } else {
                d = d + '';
            }

            day = '' + date.getFullYear() + month + d
            //day = '' + date.getFullYear() + date.getMonth() + date.getDay();

            var url = "/api/players/matt/" + day;
            $.getJSON(url, updateAvatar);

            days_ago += 1;

        }
    };
}

window.canvas = document.getElementById("doubleyou-avatar");
//console.log(window.canvas);
var processingInstance = new Processing(canvas, sketchProc);
