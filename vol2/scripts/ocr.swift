// OCR with Apple Vision. Usage: swift ocr.swift <lang e.g. en-US or ja-JP> <image> [<image> ...]
// Prints one JSON object per image: {"file": ..., "lines": [{"text", "conf", "x", "y", "w", "h"}]}
// Coordinates are normalised, origin top-left.
import Foundation
import Vision
import AppKit

let args = CommandLine.arguments
let lang = args[1]
for path in args.dropFirst(2) {
    guard let image = NSImage(contentsOfFile: path),
          let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        print("{\"file\": \"\(path)\", \"error\": \"unreadable\"}")
        continue
    }
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = [lang]
    request.usesLanguageCorrection = false
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([request])
    var lines: [[String: Any]] = []
    for obs in request.results ?? [] {
        guard let top = obs.topCandidates(1).first else { continue }
        let b = obs.boundingBox
        lines.append(["text": top.string, "conf": top.confidence,
                      "x": b.minX, "y": 1 - b.maxY, "w": b.width, "h": b.height])
    }
    let obj: [String: Any] = ["file": path, "lines": lines]
    let data = try! JSONSerialization.data(withJSONObject: obj)
    print(String(data: data, encoding: .utf8)!)
}
