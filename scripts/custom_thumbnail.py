import base64
from PyQt5.QtCore import QByteArray, QIODevice, QBuffer
from PyQt5.QtGui import QImage
import os

class CreateV2NeoThumbnail:
    def __init__(self, jpeg_path):
        self.jpeg_path = jpeg_path

    def _loadAndResizeJPEG(self, width, height):
        """Load a JPEG image from the file system and resize it to the specified width and height."""
        try:
            image = QImage(self.jpeg_path)
            if image.isNull():
                raise ValueError(f"Failed to load image from path: {self.jpeg_path}")
            
            # Resize the image to the target width and height
            resized_image = image.scaled(width, height)
            return resized_image
        except Exception as e:
            print("Error loading or resizing JPEG image:", e)

    def _encodeSnapshot(self, image):
        """Encode the image as base64."""
        try:
            thumbnail_buffer = QBuffer()
            thumbnail_buffer.open(QBuffer.ReadWrite)
            image.save(thumbnail_buffer, "JPG")
            thumbnail_data = thumbnail_buffer.data()
            thumbnail_length = thumbnail_data.length()
            base64_bytes = base64.b64encode(thumbnail_data)
            base64_message = base64_bytes.decode('ascii')
            thumbnail_buffer.close()
            print(f"Snapshot encoded, thumbnail_length={thumbnail_length}")
            return (base64_message, thumbnail_length)
        except Exception as e:
            print("Failed to encode image:", e)

    def _convertSnapshotToGcode(self, thumbnail_length, encoded_snapshot, width, height, chunk_size=76):
        """Convert base64 encoded image to G-code format."""
        gcode = []
        x1 = (int)(width / 80) + 1
        x2 = width - x1
        header = f"; jpg begin {width}*{height} {thumbnail_length} {x1} {x2} 500"
        gcode.append(header)

        chunks = [f"; {encoded_snapshot[i:i+chunk_size]}" for i in range(0, len(encoded_snapshot), chunk_size)]
        gcode.extend(chunks)

        gcode.append("; jpg end")
        gcode.append(";")
        return gcode

    def saveGcodeToFile(self, gcode, output_file):
        """Save the generated G-code to a text file."""
        try:
            with open(output_file, 'w') as f:
                f.write("\n".join(gcode))
            print(f"G-code successfully written to {output_file}")
        except Exception as e:
            print(f"Failed to write G-code to file: {e}")

    def generateThumbnailGcode(self, width, height, output_file):
        """Main function to generate the thumbnail and save G-code."""
        image = self._loadAndResizeJPEG(width, height)
        if not image:
            print("Image loading failed.")
            return

        encoded_snapshot, thumbnail_length = self._encodeSnapshot(image)
        if not encoded_snapshot:
            print("Image encoding failed.")
            return

        gcode = self._convertSnapshotToGcode(thumbnail_length, encoded_snapshot, width, height)
        self.saveGcodeToFile(gcode, output_file)


# Example usage
jpeg_path = "50_15_mL_Falcon_tray_6x6_5x5_v3.jpg"  # Path to your JPEG file
output_file = "thumbnail_gcode.txt"  # Output G-code file

thumbnail_creator = CreateV2NeoThumbnail(jpeg_path)
thumbnail_creator.generateThumbnailGcode(200, 200, output_file)
