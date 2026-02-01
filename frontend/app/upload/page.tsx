'use client';

import { useState, useRef } from 'react';
// import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Upload, FileText, Download, CheckCircle, XCircle } from 'lucide-react';

export default function UploadPage() {
  // const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [maxConcurrent, setMaxConcurrent] = useState(10);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.name.endsWith('.csv')) {
        setFile(selectedFile);
        setError(null);
        setSuccess(false);
      } else {
        setError('กรุณาเลือกไฟล์ CSV เท่านั้น');
        setFile(null);
      }
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      if (droppedFile.name.endsWith('.csv')) {
        setFile(droppedFile);
        setError(null);
        setSuccess(false);
      } else {
        setError('กรุณาเลือกไฟล์ CSV เท่านั้น');
      }
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  // Upload functionality removed as requested
  const handleUpload = () => {
    setError('ฟีเจอร์อัปโหลด CSV ถูกปิดใช้งาน');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="mb-8">
          <Link href="/" className="flex items-center text-gray-600 hover:text-gray-800 mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            กลับหน้าหลัก
          </Link>
          <h1 className="text-3xl font-bold text-gray-800">
            อัปโหลดไฟล์ CSV เพื่อประเมินความเสี่ยง
          </h1>
          <p className="text-gray-600 mt-2">
            อัปโหลดไฟล์ CSV ที่มีข้อมูลผู้ป่วยหลายรายเพื่อประมวลผลพร้อมกัน
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
              file
                ? 'border-cu-pink-400 bg-pink-50'
                : 'border-gray-300 hover:border-cu-pink-400 hover:bg-pink-50'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
              id="file-upload"
            />
            
            {!file ? (
              <label htmlFor="file-upload" className="cursor-pointer">
                <Upload className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                <p className="text-lg font-medium text-gray-700 mb-2">
                  คลิกเพื่อเลือกไฟล์ หรือ ลากไฟล์มาวางที่นี่
                </p>
                <p className="text-sm text-gray-500">
                  รองรับเฉพาะไฟล์ CSV เท่านั้น
                </p>
              </label>
            ) : (
              <div className="flex flex-col items-center">
                <FileText className="w-16 h-16 text-cu-pink-600 mb-4" />
                <p className="text-lg font-medium text-gray-800 mb-1">
                  {file.name}
                </p>
                <p className="text-sm text-gray-500 mb-4">
                  {(file.size / 1024).toFixed(2)} KB
                </p>
                <button
                  onClick={() => {
                    setFile(null);
                    if (fileInputRef.current) {
                      fileInputRef.current.value = '';
                    }
                  }}
                  className="text-red-600 hover:text-red-700 text-sm font-medium"
                >
                  ลบไฟล์
                </button>
              </div>
            )}
          </div>

          {/* Settings */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <label className="block text-gray-700 font-medium mb-2">
              จำนวน Concurrent Requests (ความเร็วในการประมวลผล)
            </label>
            <div className="flex items-center space-x-4">
              <input
                type="range"
                min="1"
                max="20"
                value={maxConcurrent}
                onChange={(e) => setMaxConcurrent(parseInt(e.target.value))}
                className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <span className="text-2xl font-bold text-cu-pink-600 w-16 text-center">
                {maxConcurrent}
              </span>
            </div>
            <p className="text-sm text-gray-500 mt-2">
              ค่าที่แนะนำ: 10 (เพิ่มได้ถึง 20 แต่ระวัง API rate limit)
            </p>
          </div>



          {/* Error Message */}
          {error && (
            <div className="mt-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start">
              <XCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium">เกิดข้อผิดพลาด</p>
                <p className="text-sm">{error}</p>
              </div>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="mt-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg flex items-start">
              <CheckCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium">ประมวลผลสำเร็จ!</p>
                <p className="text-sm">ไฟล์ผลลัพธ์ได้ถูกดาวน์โหลดแล้ว</p>
              </div>
            </div>
          )}

          {/* Upload Button (disabled) */}
          <button
            onClick={handleUpload}
            disabled={true}
            className="w-full mt-6 flex items-center justify-center px-6 py-4 bg-gray-300 text-white rounded-lg font-medium cursor-not-allowed"
          >
            <Upload className="w-5 h-5 mr-2" />
            ฟีเจอร์อัปโหลด CSV ถูกปิดใช้งาน
          </button>
        </div>

        {/* Instructions */}
        <div className="bg-white rounded-lg shadow-md p-6 mt-8">
          <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
            <Download className="w-5 h-5 mr-2 text-cu-pink-600" />
            วิธีใช้งาน
          </h3>
          <ol className="space-y-3 text-gray-700">
            <li className="flex items-start">
              <span className="font-bold text-cu-pink-600 mr-2">1.</span>
              <span>เตรียมไฟล์ CSV ที่มีคอลัมน์ตามคำถาม 27 ข้อ (ดูตัวอย่างจาก data/66.csv)</span>
            </li>
            <li className="flex items-start">
              <span className="font-bold text-cu-pink-600 mr-2">2.</span>
              <span>อัปโหลดไฟล์ CSV โดยคลิกหรือลากไฟล์มาวาง</span>
            </li>
            <li className="flex items-start">
              <span className="font-bold text-cu-pink-600 mr-2">3.</span>
              <span>ปรับจำนวน Concurrent Requests ตามต้องการ (เริ่มต้นแนะนำ 10)</span>
            </li>
            <li className="flex items-start">
              <span className="font-bold text-cu-pink-600 mr-2">4.</span>
              <span>กดปุ่ม &quot;อัปโหลดและประเมินความเสี่ยง&quot;</span>
            </li>
            <li className="flex items-start">
              <span className="font-bold text-cu-pink-600 mr-2">5.</span>
              <span>รอการประมวลผลเสร็จ ไฟล์ผลลัพธ์จะถูกดาวน์โหลดอัตโนมัติ</span>
            </li>
          </ol>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <h4 className="font-bold text-gray-800 mb-2">รูปแบบไฟล์ CSV</h4>
            <p className="text-sm text-gray-600">
              ไฟล์ CSV ต้องมีคอลัมน์ตามคำถาม 27 ข้อ โดยใช้ชื่อคอลัมน์ตามที่กำหนดใน types.ts
              เช่น age, gender, hn, pain_score, fever_status ฯลฯ
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
