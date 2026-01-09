import qrcode

# Generate QR code for the new URL
url = "https://rent-verify-bot.onrender.com"

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

qr.add_data(url)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("assets/qr_rent-verify-bot.png")

print(f"QR code generated successfully for: {url}")
print("Saved to: assets/qr_rent-verify-bot.png")
