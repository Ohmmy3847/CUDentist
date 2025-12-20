import Link from 'next/link';
import { FileUp, FileText } from 'lucide-react';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
            ระบบประเมินความเสี่ยงผู้ป่วยหลังผ่าตัด
          </h1>
          <p className="text-xl text-gray-600">
            Post-Operative Patient Risk Assessment System
          </p>
        </div>

        {/* Options */}
        <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-8">
          {/* Form Option */}
          <Link href="/form">
            <div className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-8 cursor-pointer border-2 border-transparent hover:border-cu-pink-500 group">
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="p-6 bg-pink-100 rounded-full group-hover:bg-cu-pink-500 transition-colors duration-300">
                  <FileText className="w-16 h-16 text-cu-pink-600 group-hover:text-white transition-colors duration-300" />
                </div>
                <h2 className="text-2xl font-bold text-gray-800">กรอกแบบฟอร์ม</h2>
                <p className="text-gray-600">
                  กรอกข้อมูลผู้ป่วยด้วยตนเองผ่านแบบฟอร์ม 27 คำถาม
                </p>
                <div className="pt-4">
                  <span className="inline-block px-6 py-3 bg-pink-600 text-white rounded-lg group-hover:bg-pink-700 transition-colors duration-300">
                    เริ่มกรอกฟอร์ม →
                  </span>
                </div>
              </div>
            </div>
          </Link>

          {/* CSV Upload Option */}
          <Link href="/upload" aria-disabled="true" className="pointer-events-none cursor-not-allowed"  >
            <div className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-8 cursor-not-allowed border-2 border-transparent hover:border-yellow-500 group opacity-50">
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="p-6 bg-yellow-100 rounded-full group-hover:bg-yellow-500 transition-colors duration-300">
                  <FileUp className="w-16 h-16 text-yellow-600 group-hover:text-white transition-colors duration-300" />
                </div>
                <h2 className="text-2xl font-bold text-gray-800">อัปโหลด CSV</h2>
                <p className="text-gray-600">
                  อัปโหลดไฟล์ CSV สำหรับประเมินผู้ป่วยหลายรายพร้อมกัน
                </p>
                <div className="pt-4">
                  <span className="inline-block px-6 py-3 bg-yellow-500 text-white rounded-lg group-hover:bg-yellow-600 transition-colors duration-300">
                    อัปโหลดไฟล์ →
                  </span>
                </div>
              </div>
            </div>
          </Link>
        </div>
        {/* Info Section */}
        <div className="max-w-3xl mx-auto mt-16 bg-white rounded-xl shadow-md p-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-4">เกี่ยวกับระบบ</h3>
          <ul className="space-y-3 text-gray-700">
            <li className="flex items-start">
              <span className="text-cu-pink-600 mr-2">✓</span>
              <span>ประเมินความเสี่ยงผู้ป่วยหลังผ่าตัดทันตกรรม</span>
            </li>
            <li className="flex items-start">
              <span className="text-cu-pink-600 mr-2">✓</span>
              <span>จำแนกระดับความเสี่ยง: ต่ำ, กลาง, สูง</span>
            </li>
            <li className="flex items-start">
              <span className="text-cu-pink-600 mr-2">✓</span>
              <span>ให้คำแนะนำการดูแลตนเองตามระดับความเสี่ยง</span>
            </li>
            <li className="flex items-start">
              <span className="text-cu-pink-600 mr-2">✓</span>
              <span>รองรับการประมวลผลแบบ Batch ผ่าน CSV</span>
            </li>
          </ul>
        </div>
      </div>
    </main>
  );
}
