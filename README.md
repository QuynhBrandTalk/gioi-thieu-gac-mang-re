# Gạc Măng Rê — site giới thiệu

Site tĩnh, deploy qua GitHub Pages. Sửa link liên hệ trong `js/site.js`.

## Thêm hoặc xuất bản một Ngăn

1. Tạo hoặc sửa file trong `content/ngan/` (mỗi Ngăn một file JSON).
2. Chạy `python3 tools/build.py` từ thư mục gốc.
3. Ngăn có `"publish": false` chỉ hiện thẻ "Sắp có" trên trang chủ.
4. Ngăn `"publish": true` chỉ được sinh trang khi đủ ảnh và đoạn văn ở cả bốn chương. Thiếu gì, script báo tên chương và không sinh trang.
