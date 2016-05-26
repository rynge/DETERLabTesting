node {
   // Mark the code checkout 'stage'....
   stage 'Checkout'
   git url: 'https://github.com/rynge/DETERLabTesting.git'
   sh 'git clean -fdx'

   // 001
   stage '001'
   sh "./run-test mrynge pegasus 001"
   step([$class: 'JUnitResultArchiver', keepLongStdio: true, testResults: 'reports/001/*.xml'])
   
   // 002
   stage '002'
   sh "./run-test mrynge pegasus 002"
   step([$class: 'JUnitResultArchiver', keepLongStdio: true, testResults: 'reports/002/*.xml'])
   
   // 003
   stage '003'
   sh "./run-test mrynge pegasus 003"
   step([$class: 'JUnitResultArchiver', keepLongStdio: true, testResults: 'reports/003/*.xml'])

}

