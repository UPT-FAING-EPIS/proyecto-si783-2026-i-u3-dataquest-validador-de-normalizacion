const fs = require('fs');
const path = require('path');

function copyFolderSync(from, to) {
    if (!fs.existsSync(to)) {
        fs.mkdirSync(to, { recursive: true });
    }
    const elements = fs.readdirSync(from);
    for (const element of elements) {
        if (element === '__pycache__' || element === '.pytest_cache') continue;
        
        const stat = fs.lstatSync(path.join(from, element));
        if (stat.isFile()) {
            fs.copyFileSync(path.join(from, element), path.join(to, element));
        } else if (stat.isDirectory()) {
            copyFolderSync(path.join(from, element), path.join(to, element));
        }
    }
}

const source = path.join(__dirname, '..', 'core');
const dest = path.join(__dirname, 'core');

console.log(`Copiando el motor Python desde ${source} hacia ${dest}...`);
copyFolderSync(source, dest);
console.log('¡Copia completada con éxito!');
