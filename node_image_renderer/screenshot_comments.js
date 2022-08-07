const nodeHtmlToImage = require('node-html-to-image')
const {program} = require('commander')
const compile = require('es6-template-strings/compile')
const resolveToString = require('es6-template-strings/resolve-to-string')
const fs = require('fs')
const path = require('path');
const Path = require("path");

// Read html template
const template_path = Path.join(global.__basedir = __dirname, "comment_template.html")
const compiledHTML = compile(fs.readFileSync(template_path, "utf-8"))


// Check whether the content text is valid
const isTextValid = (text) => {
    return text.length <= 1000 && !text.includes("http")
}

const save_comment = (
    filename,
    comment,
    reply
) => {

    const author = comment["author"]
    const content = comment["content"]
    const score = comment["score"]
    const reply_author = reply?.author
    const reply_content = reply?.content
    const invisible_reply = reply?.hide
    const reply_score = reply?.score
    const hasReply = reply_author !== undefined && reply_content !== undefined

    let parsed_html = resolveToString(compiledHTML,
        {
            author,
            content,
            score,
            reply_author,
            reply_content,
            reply_score,
            reply_display_class: hasReply ? "" : "d-none",
            invisible_class: invisible_reply ? "invisible" : ""
        });

    nodeHtmlToImage({
        output: filename,
        html: parsed_html
    })
}


// Parse arguments
program
    .option('--path <string>')
    .option(' --json <string>')
    .option(' --max <number>')

program.parse()

const options = program.opts()
const save_path = options.path // The path to save the images
const json = options.json // The path to the json file that contains the comments
const max_comments = options.max // The path to the json file that contains the comments

// Load json file
let raw = fs.readFileSync(json)
let comments = JSON.parse(raw)

let comments_iterated = 0


for (const [author, comment] of Object.entries(comments["comments"])) {
    // Where to save the images
    let base_dir = Path.join(save_path, author)
    // If we reached the max comments number
    if (comments_iterated >= max_comments) break

    let content = comment["text"]
    if (!isTextValid(content)) continue

    // If the save directory doesn't exist, create it
    if (!fs.existsSync(base_dir)) fs.mkdirSync(base_dir, {recursive: true})

    // Get reply
    let reply;
    let replies = comment["replies"];
    if (Object.keys(replies).length !== 0) {
        // if (Object.keys(replies).length !== 0 && Math.round(Math.random()) === 1) {
        let _ = Object.entries(replies)[0] // Only get first reply
        if (isTextValid(_[1]["text"])) {
            reply = _
        }
    }

    let commentData = {
        author: author,
        content: content,
        score: comment["score"]
    }

    let replyData
    if (reply)
        replyData = {
            author: reply[0],
            content: reply ? reply[1]["text"] : "",
            score: reply ? reply[1]["score"] : "",
            hide: true
        }

    save_comment(path.join(base_dir, "1.png"), commentData, replyData)
    if (reply) {
        replyData.hide = false
        save_comment(path.join(base_dir, "2.png"), commentData, replyData)
    }

    comments_iterated++
}

console.log("Comments saved!")
