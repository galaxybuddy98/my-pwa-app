"use client";

import Image from "next/image";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-between px-4 py-8 bg-white">
      {/* 상단 타이틀 */}
      <header className="text-center mt-8">
        <h1 className="text-2xl font-semibold">📂 프로젝트3 - 대희</h1>
      </header>

      {/* 중앙 비어있는 공간 */}
      <main className="flex-1 flex items-center justify-center w-full"></main>

      {/* 하단 입력창 */}
      <footer className="w-full max-w-2xl mb-6">
        <div className="relative bg-[#f6f6f6] rounded-2xl px-4 py-3 border border-gray-200 shadow-sm flex items-center">
          <input
            type="text"
            placeholder="프로젝트3 - 대희에서 새 채팅"
            className="flex-1 bg-transparent text-sm outline-none placeholder-gray-500"
          />
          <div className="flex items-center space-x-2 ml-3">
            {/* 도구 아이콘 (예시 이미지처럼 추가 아이콘 표시) */}
            <button className="text-gray-500 hover:text-black">
              <span className="text-sm">⚙️ 도구</span>
            </button>
            <button className="text-gray-500 hover:text-black">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 10l4.553 2.276a1 1 0 010 1.448L15 16m0 0v4m0-4H9m6 0H9m0 0v-4m0 0L4.447 13.724a1 1 0 010-1.448L9 10"
                />
              </svg>
            </button>
            <button className="text-gray-500 hover:text-black">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}
