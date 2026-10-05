import Foundation
import Vision
import AppKit

// vocr2: Vision OCR 带坐标输出（表格重建用）
// 输出格式: y_center x_center  text （图片坐标归一化 0-1，y 从上到下）
let path = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "/tmp/sheet.png"
guard let img = NSImage(contentsOfFile: path),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("ERROR: cannot load image")
    exit(1)
}

let request = VNRecognizeTextRequest { req, err in
    guard let results = req.results as? [VNRecognizedTextObservation] else { return }
    let sorted = results.sorted { a, b in
        let ay = a.boundingBox.origin.y + a.boundingBox.height / 2
        let by = b.boundingBox.origin.y + b.boundingBox.height / 2
        if abs(ay - by) > 0.015 { return ay > by }
        return a.boundingBox.origin.x < b.boundingBox.origin.x
    }
    for obs in sorted {
        if let top = obs.topCandidates(1).first {
            let y = 1.0 - (obs.boundingBox.origin.y + obs.boundingBox.height / 2) // 0=顶部
            let x = obs.boundingBox.origin.x + obs.boundingBox.width / 2
            print(String(format: "%.4f %.4f %@", y, x, top.string))
        }
    }
}
request.recognitionLevel = .accurate
request.recognitionLanguages = ["zh-Hans", "en-US"]
request.usesLanguageCorrection = true

let handler = VNImageRequestHandler(cgImage: cg, options: [:])
try? handler.perform([request])
