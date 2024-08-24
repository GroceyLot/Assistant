import tkinter as tk
from PIL import Image, ImageTk
import time


class Window:
    def __init__(self, root: tk.Tk, cornerImagePath, edgeImagePath):
        self.root = root
        self.cornerImagePath = cornerImagePath
        self.edgeImagePath = edgeImagePath
        self.cornerSize = 20  # Size of the corner image (20x20)
        self.edgeHeight = 20  # Height of the edge image (20px tall)

        # Load and resize images
        self.cornerImage = Image.open(self.cornerImagePath).resize(
            (self.cornerSize, self.cornerSize)
        )
        self.edgeImage = Image.open(self.edgeImagePath).resize(
            (self.edgeHeight, self.edgeHeight)
        )

        # Pre-create rotated images
        self.cornerImages = {
            "topLeft": ImageTk.PhotoImage(self.cornerImage),
            "topRight": ImageTk.PhotoImage(self.cornerImage.rotate(270)),
            "bottomLeft": ImageTk.PhotoImage(self.cornerImage.rotate(90)),
            "bottomRight": ImageTk.PhotoImage(self.cornerImage.rotate(180)),
        }

        self.edgeImages = {
            "top": ImageTk.PhotoImage(self.edgeImage),
            "bottom": ImageTk.PhotoImage(self.edgeImage.rotate(180)),
            "left": ImageTk.PhotoImage(self.edgeImage.rotate(90)),
            "right": ImageTk.PhotoImage(self.edgeImage.rotate(270)),
        }

        # Create the window without a title bar
        self.root.overrideredirect(True)
        self.root.geometry(
            "400x300+100+100"
        )  # Set initial size to 400x300 pixels, positioned at (100,100)
        self.root.attributes("-topmost", True)  # Keep the window on top
        self.root.attributes("-transparentcolor", "white")  # Set transparency color
        self.root.configure(bg="#262930")  # Set the background color

        # Create a canvas to draw the window's borders and corners
        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Initial draw
        self.drawWindow()

        # Make the window draggable
        self.root.bind("<Button-1>", self.startMove)
        self.root.bind("<B1-Motion>", self.doMove)

        # Re-draw the window on resize
        self.root.bind("<Configure>", self.onResize)

    def drawWindow(self):
        # Get the current window size
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # Clear the canvas
        self.canvas.delete("all")

        # Draw corners
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.cornerImages["topLeft"])
        self.canvas.create_image(
            width, 0, anchor=tk.NE, image=self.cornerImages["topRight"]
        )
        self.canvas.create_image(
            0, height, anchor=tk.SW, image=self.cornerImages["bottomLeft"]
        )
        self.canvas.create_image(
            width, height, anchor=tk.SE, image=self.cornerImages["bottomRight"]
        )

        # Draw edges
        for x in range(self.cornerSize, width - self.cornerSize, self.edgeHeight):
            self.canvas.create_image(x, 0, anchor=tk.NW, image=self.edgeImages["top"])
            self.canvas.create_image(
                x, height, anchor=tk.SW, image=self.edgeImages["bottom"]
            )

        for y in range(self.cornerSize, height - self.cornerSize, self.edgeHeight):
            self.canvas.create_image(0, y, anchor=tk.NW, image=self.edgeImages["left"])
            self.canvas.create_image(
                width, y, anchor=tk.NE, image=self.edgeImages["right"]
            )

        # Draw the filled rectangle inside the edges
        self.canvas.create_rectangle(
            self.cornerSize,
            self.cornerSize,
            width - self.cornerSize,
            height - self.cornerSize,
            fill="#262930",
            outline="",
        )

        # Keep a reference to the images to prevent garbage collection
        self.root.image_refs = list(self.cornerImages.values()) + list(
            self.edgeImages.values()
        )

    def onResize(self, event):
        self.drawWindow()

    def startMove(self, event):
        self.x = event.x
        self.y = event.y

    def doMove(self, event):
        x = event.x_root - self.x
        y = event.y_root - self.y
        self.root.geometry(f"+{x}+{y}")

    def move(self, newGeometry, duration):
        currentGeometry = self.root.geometry()
        currentWidth, currentHeight, currentX, currentY = map(
            int, currentGeometry.replace("x", "+").split("+")
        )
        newWidth, newHeight, newX, newY = map(
            int, newGeometry.replace("x", "+").split("+")
        )

        startTime = time.time()

        def update():
            elapsed = time.time() - startTime
            if elapsed > duration:
                elapsed = duration

            fraction = elapsed / duration
            currentW = int(currentWidth + (newWidth - currentWidth) * fraction)
            currentH = int(currentHeight + (newHeight - currentHeight) * fraction)
            currentXPos = int(currentX + (newX - currentX) * fraction)
            currentYPos = int(currentY + (newY - currentY) * fraction)

            self.root.geometry(f"{currentW}x{currentH}+{currentXPos}+{currentYPos}")

            self.root.update_idletasks()
            self.root.update()

            self.drawWindow()

            if elapsed < duration:
                self.root.after(1, update)

        update()
