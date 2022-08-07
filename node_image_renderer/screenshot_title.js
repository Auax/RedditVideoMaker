const nodeHtmlToImage = require('node-html-to-image')
const {program} = require('commander')
const compile = require('es6-template-strings/compile')
const resolveToString = require('es6-template-strings/resolve-to-string')
const fs = require('fs')
const Path = require("path");

// Read html template
const template_path = Path.join(global.__basedir = __dirname, "title_template.html")
const compiledHTML = compile(fs.readFileSync(template_path, "utf-8"))


const save_title = (
    filename,
    title,
    author,
    score,
) => {
    let parsed_html = resolveToString(compiledHTML,
        {
            title,
            author,
            score
        });

    nodeHtmlToImage({
        output: filename,
        html: parsed_html
    })
}


// Parse arguments
program
    .option('--path <string>')
    .option(' --title <string>')
    .option(' --author <number>')
    .option(' --score <number>')

program.parse()

const options = program.opts()
const save_path = options.path // The path to save the images
const title = options.title
const author = options.author
const score = options.score


// If the save directory doesn't exist, create it
if (!fs.existsSync(save_path)) fs.mkdirSync(save_path, {recursive: true})
save_title(
    Path.join(save_path, "title.png"),
    title,
    author,
    score
)

console.log("Title saved!")