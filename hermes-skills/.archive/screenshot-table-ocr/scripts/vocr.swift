import Foundation
import Vision
import AppKit

// macOS Vision framework OCR 兜底脚本
// 用途：tesseract 对复杂/深色/半透明截图失效时的中文 OCR 备选
// 编译：swiftc -O vocr.swift -o vocr
// 运行：./vocr <图片路径>
// 注意：对纯文字截图有效；图形化卡片（文字是渲染图形）仍可能失败

let path = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "/tmp/sheet_restored.png"
guard let img = NSImage(contentsOfFile: path),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("ERROR: cannot load image")
    exit(1)
}

let request = VNRecognizeTextRequest { req, err in
    guard let results = req.results as? [VNRecognizedTextObservation] else { return }
    // 按 y 坐标排序（从上到下）
    let sorted = results.sorted { a, b in
        let ay = a.boundingBox.origin.y
        let by = b.boundingBox.origin.y
        if abs(ay - by) > 0.02 { return ay > by }
        return a.boundingBox.origin.x < b.boundingBox.origin.x
    }
    for obs in sorted {
        if let top = obs.topCandidates(1).first {
            print(top.string)
        }
    }
}
request.recognitionLevel = .accurate
request.recognitionLanguages = ["zh-Hans", "en-US"]
request.usesLanguageCorrection = true

let handler = VNImageRequestHandler(cgImage: cg, options: [:])
try? handler.perform([request])
