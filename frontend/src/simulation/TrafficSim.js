/**
 * Navi Framework — Traffic Telemetry Simulation Engine
 * Canvas-based visualization of intersection signal phases
 */

export class TrafficSim {
    constructor(canvas, greenTimes = [30, 30, 30, 30], themeColor = "#10b981", congestionPressure = 80, avgSpeed = 2.8) {
        this.canvas = canvas;
        this.ctx = canvas.getContext("2d");
        this.greenTimes = greenTimes; 
        this.themeColor = themeColor;
        this.pressure = congestionPressure;
        this.running = true; 
        
        this.lanes = [
            { id: "North", cars: [], direction: [0, 1], spawnX: 375, spawnY: -50, stopY: 200, name: "NORTH" },
            { id: "South", cars: [], direction: [0, -1], spawnX: 410, spawnY: 550, stopY: 300, name: "SOUTH" },
            { id: "East", cars: [], direction: [1, 0], spawnX: -50, spawnY: 212, stopX: 350, name: "EAST" },
            { id: "West", cars: [], direction: [-1, 0], spawnX: 850, spawnY: 257, stopX: 450, name: "WEST" },
        ];

        this.currentLane = 0;
        this.cycleTimer = 0;
        this.maxSpeed = Math.max(1.5, Math.min(4.5, avgSpeed)); 
        this.carSpacing = 32;

        this.metrics = {
            avgWait: 0,
            throughput: 0,
            activeCars: 0,
            queueLength: 0
        };

        this.carColors = ["#10b981", "#3b82f6", "#f59e0b", "#f43f5e", "#8b5cf6", "#22d3ee", "#ffffff"];
    }

    update(dt) {
        if (!this.running) return;

        this.cycleTimer += dt / 1000;
        const currentPhaseDuration = this.greenTimes[this.currentLane] || 30;
        
        if (this.cycleTimer >= currentPhaseDuration) {
            this.cycleTimer = 0;
            this.currentLane = (this.currentLane + 1) % 4;
        }

        // Spawn Logic (Tied to Pressure)
        const spawnProbability = Math.min(0.12, 0.04 + (this.pressure / 2000));
        if (Math.random() < spawnProbability) {
            this.spawnCar(Math.floor(Math.random() * 4));
        }

        this.metrics.queueLength = 0;
        this.lanes.forEach((lane, idx) => {
            const isGreen = this.currentLane === idx;
            
            for (let i = 0; i < lane.cars.length; i++) {
                const car = lane.cars[i];
                const nextCar = i > 0 ? lane.cars[i - 1] : null; 
                let targetSpeed = this.maxSpeed;

                const atLight = this.isAtLight(car, lane);
                
                if (!isGreen && atLight) {
                    targetSpeed = 0;
                    this.metrics.queueLength++;
                }

                if (nextCar) {
                    const dist = this.getDistance(car, nextCar);
                    if (dist < this.carSpacing) {
                        targetSpeed = Math.min(nextCar.speed, targetSpeed);
                        if (nextCar.speed < 0.1) targetSpeed = 0;
                    }
                }

                car.speed += (targetSpeed - car.speed) * 0.15;
                if (car.speed < 0.01) car.speed = 0;
                
                car.x += car.vx * car.speed;
                car.y += car.vy * car.speed;
            }

            // Safe removal of out-of-bounds vehicles without index corruption
            const initialCount = lane.cars.length;
            lane.cars = lane.cars.filter(car => car.x >= -150 && car.x <= 950 && car.y >= -150 && car.y <= 650);
            const exited = initialCount - lane.cars.length;
            this.metrics.throughput += exited;
        });

        this.metrics.activeCars = this.lanes.reduce((acc, l) => acc + l.cars.length, 0);
    }

    spawnCar(laneIdx) {
        const lane = this.lanes[laneIdx];
        if (lane.cars.length > 0) {
            const last = lane.cars[lane.cars.length - 1];
            const dist = Math.sqrt((last.x - lane.spawnX)**2 + (last.y - lane.spawnY)**2);
            if (dist < 45) return;
        }

        lane.cars.push({
            x: lane.spawnX,
            y: lane.spawnY,
            vx: lane.direction[0],
            vy: lane.direction[1],
            speed: this.maxSpeed,
            color: this.carColors[Math.floor(Math.random() * this.carColors.length)],
            width: lane.direction[0] === 0 ? 14 : 22,
            height: lane.direction[0] === 0 ? 22 : 14,
        });
    }

    isAtLight(car, lane) {
        if (lane.id === "North") return car.y >= lane.stopY - 25 && car.y < lane.stopY + 5;
        if (lane.id === "South") return car.y <= lane.stopY + 25 && car.y > lane.stopY - 5;
        if (lane.id === "East") return car.x >= lane.stopX - 25 && car.x < lane.stopX + 5;
        if (lane.id === "West") return car.x <= lane.stopX + 25 && car.x > lane.stopX - 5;
        return false;
    }

    getDistance(c1, c2) {
        return Math.sqrt((c1.x - c2.x)**2 + (c1.y - c2.y)**2);
    }

    draw() {
        if (!this.ctx || !this.canvas) return;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // 1. Road Background
        this.ctx.fillStyle = "#08080a";
        this.ctx.fillRect(0, 0, 800, 500);

        this.ctx.fillStyle = "#121215";
        this.ctx.fillRect(360, 0, 80, 500); 
        this.ctx.fillRect(0, 200, 800, 100); 

        // Lane Markings
        this.ctx.strokeStyle = "rgba(255,255,255,0.05)";
        this.ctx.setLineDash([10, 15]);
        this.ctx.lineWidth = 1;
        this.ctx.beginPath();
        this.ctx.moveTo(400, 0); this.ctx.lineTo(400, 500);
        this.ctx.moveTo(0, 250); this.ctx.lineTo(800, 250);
        this.ctx.stroke();
        this.ctx.setLineDash([]);

        // 2. Signals
        const lights = [
            { id: 0, x: 380, y: 185 }, 
            { id: 1, x: 420, y: 315 }, 
            { id: 2, x: 345, y: 265 }, 
            { id: 3, x: 455, y: 235 }, 
        ];

        lights.forEach((l, i) => {
            const isGreen = this.currentLane === i;
            if (isGreen) {
                this.ctx.shadowBlur = 18;
                this.ctx.shadowColor = this.themeColor;
            }
            this.ctx.beginPath();
            this.ctx.arc(l.x, l.y, 8, 0, Math.PI * 2);
            this.ctx.fillStyle = isGreen ? this.themeColor : "#3a1515";
            this.ctx.fill();
            this.ctx.shadowBlur = 0;
        });

        // 3. Vehicles
        this.lanes.forEach(lane => {
            lane.cars.forEach(car => {
                this.ctx.fillStyle = car.color;
                this.ctx.beginPath();
                if (this.ctx.roundRect) {
                    this.ctx.roundRect(car.x - car.width/2, car.y - car.height/2, car.width, car.height, 4);
                } else {
                    this.ctx.rect(car.x - car.width/2, car.y - car.height/2, car.width, car.height);
                }
                this.ctx.fill();
            });
        });
    }
}
