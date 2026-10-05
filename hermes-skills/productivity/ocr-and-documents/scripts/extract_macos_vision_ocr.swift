#!/usr/bin/swift
/// macOS Vision OCR — extract text from scanned PDFs using Apple's Vision framework.
/// Works offline, zero dependencies (shipped with macOS).
///
/// Usage:
///   swift extract_macos_vision_ocr.swift <image_or_pdf_path>
///   swift extract_macos_vision_ocr.swift <path> --lang zh-Hans,en
///
/// For PDFs: extracts embedded images first, then OCRs each page.
/// For images: OCRs directly.
///
/// Output: sorted text (top-to-bottom, left-to-right) to stdout.

import Cocoa
import Vision

// ── Parse args ──────────────────────────────────────────
let args = CommandLine.arguments.dropFirst()
guard let path = args.first else {
    print("Usage: swift extract_macos_vision_ocr.swift <pdf_or_image_path> [--lang lang1,lang2]")
    exit(1)
}

let langArg = args.first(where: { $0 == "--lang" })
let langIdx = args.firstIndex(of: "--lang")
let languages: [String] = {
    if let idx = langIdx, idx + 1 < args.count {
        return args[args.index(after: idx)].split(separator: ",").map(String.init)
    }
    return ["zh-Hans", "en"]
}()

// ── OCR a single CGImage ────────────────────────────────
func ocr(_ cgImage: CGImage) -> [String] {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    request.recognitionLanguages = languages

    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    try! handler.perform([request])

    guard let observations = request.results, !observations.isEmpty else {
        return []
    }

    // Sort top-to-bottom, then left-to-right
    let sorted = observations.sorted { a, b in
        let ab = a.boundingBox.origin.y
        let bb = b.boundingBox.origin.y
        if abs(ab - bb) < 0.02 {
            return a.boundingBox.origin.x < b.boundingBox.origin.x
        }
        return ab > bb
    }

    return sorted.compactMap { $0.topCandidates(1).first?.string }
}

// ── OCR a PDF page (extract embedded images) ────────────
func ocrPDFPage(_ page: NSPDFPage, index: Int) -> [String] {
    // Render the page to an image
    let box = page.bounds(for: .mediaBox)
    let image = NSImage(size: box.size)
    image.lockFocus()
    let ctx = NSGraphicsContext.current!
    ctx.cgContext.setFillColor(NSColor.white.cgColor)
    ctx.cgContext.fill(CGRect(origin: .zero, size: box.size))
    page.draw(with: .mediaBox)
    image.unlockFocus()

    guard let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        print("  [Page \(index + 1)] Could not render")
        return []
    }

    return ocr(cgImage)
}

// ── Main ────────────────────────────────────────────────
let url = URL(fileURLWithPath: path)
let ext = url.pathExtension.lowercased()

if ext == "pdf" {
    guard let pdf = NSPDFImageRep(contentsOf: url) else {
        print("Could not open PDF: \(path)")
        exit(1)
    }
    let count = pdf.pageCount
    print("=== OCR: \(count) page(s) ===")
    for i in 0..<count {
        pdf.currentPage = i
        guard let cgImage = pdf.cgImage(at: .zero, for: .zero, bestFor: .zero) else {
            print("  [Page \(i + 1)] Could not render")
            continue
        }
        let lines = ocr(cgImage)
        print("\n--- Page \(i + 1)/\(count) ---")
        for line in lines {
            print(line)
        }
    }
} else {
    // Image file — try NSImage first
    guard let image = NSImage(contentsOf: url),
          let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        print("Could not open image: \(path)")
        exit(1)
    }
    let lines = ocr(cgImage)
    for line in lines {
        print(line)
    }
}
